#!/usr/bin/env python3
"""
Vinicio V. — TaskRabbit monitor bot
===================================
Scrapes Vinicio's public TaskRabbit profile (stats, work photos, and written
reviews), diffs against data/profile-stats.json, downloads any new gallery
images, and rewrites the JSON. The website reads that JSON at runtime.

Run:
    python3 monitor.py            # update locally, print a report
    python3 monitor.py --push     # also git commit + push (deploy)
    python3 monitor.py --dry      # fetch + diff only, never write

Exit code 0 = ran (whether or not data changed). Non-zero = hard failure.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import requests

PROFILE_URL = "https://www.taskrabbit.com/profile/vinicio-v--2"
TRPC_REVIEWS = "https://www.taskrabbit.com/next-api/trpc/page.tasker.categoryReviews"
ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "profile-stats.json"
CHANGELOG = ROOT / "data" / "changelog.json"
GALLERY_DIR = ROOT / "public" / "gallery"
MAX_GALLERY = 12  # newest photos kept on the site

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/html,*/*",
}

# Stable copy used when live scrape omits a field. Services/blurbs are merged
# with live rates + job counts when available.
STATIC = {
    "name": "Vinicio V.",
    "bio": (
        "Part-time Tasker helping pay off student loans — and genuinely "
        "enjoying the work. Integrity and hard work come first. Two-hour "
        "minimum on most tasks."
    ),
    "services": [
        {"name": "Yard Work", "count": 21, "price": "$53.68/hr",
         "blurb": "Mowing, edging, planting, clean-up and landscaping."},
        {"name": "Cleaning", "count": 35, "price": "$53.68/hr",
         "blurb": "Deep cleans, move-in/out, organizing — detail-obsessed."},
        {"name": "Moving Help", "count": 13, "price": "$48.52/hr",
         "blurb": "Loading, unloading, in-home moves, furniture."},
        {"name": "Car Washing", "count": 7, "price": "$48.52/hr",
         "blurb": "Interior + exterior detailing at your place."},
        {"name": "Estate Cleanout", "count": 5, "price": "$50/hr",
         "blurb": "Whole-home clear-outs, sorting, removal."},
        {"name": "Laundry Service", "count": 1, "price": "$52.65/hr",
         "blurb": "Wash, fold, and closet organization."},
    ],
    "avatar": "public/profile.jpg",
    "travelFee": {
        "feeWaived": True,
        "label": "Travel fee temporarily waived",
        "sublabel": "No extra charge for jobs in the Seattle area right now.",
    },
}

# Map TaskRabbit category names → site service names / blurbs
SERVICE_ALIASES = {
    "Yard Work": "Yard Work",
    "Cleaning": "Cleaning",
    "Help Moving": "Moving Help",
    "Car Washing": "Car Washing",
    "Trash & Furniture Removal": "Estate Cleanout",
    "Laundry and Ironing": "Laundry Service",
}

SERVICE_BLURBS = {s["name"]: s["blurb"] for s in STATIC["services"]}


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def _parse_job_count(attributes) -> int | None:
    if not attributes:
        return None
    for attr in attributes:
        label = attr.get("label") or ""
        m = re.search(r"^(\d+)\s+", label)
        if m and "overall" not in label.lower():
            return int(m.group(1))
    return None


def scrape_profile(session: requests.Session) -> dict:
    """Return live profile fields + raw categories from __NEXT_DATA__."""
    r = session.get(PROFILE_URL, timeout=45)
    r.raise_for_status()
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        r.text,
        re.S,
    )
    if not m:
        raise ValueError("Could not find __NEXT_DATA__ on profile page")

    page = json.loads(m.group(1))["props"]["pageProps"]["page"]["bff"]
    rating = page.get("rating") or {}
    reviews_raw = rating.get("totalReviews") or ""
    reviews_m = re.search(r"(\d+)", reviews_raw)
    reviews = int(reviews_m.group(1)) if reviews_m else 0

    since_m = re.search(r"Tasker since (\d{4})", r.text)
    since = int(since_m.group(1)) if since_m else None

    metro = page.get("metroName") or "Seattle"
    vehicles = (page.get("vehiclesDisplay") or "").replace("Vehicles: ", "").strip()

    photos = []
    seen_ids = set()
    for cat in page.get("categories") or []:
        items = ((cat.get("categoryPhotos") or {}).get("items")) or []
        for item in items:
            pid = item.get("id")
            url = item.get("imageUrl")
            if not pid or not url or pid in seen_ids:
                continue
            seen_ids.add(pid)
            photos.append({
                "id": pid,
                "url": url,
                "category": cat.get("name") or "",
            })
    # Newest photo IDs first
    photos.sort(key=lambda p: p["id"], reverse=True)

    services = []
    for cat in page.get("categories") or []:
        site_name = SERVICE_ALIASES.get(cat.get("name") or "")
        if not site_name:
            continue
        count = _parse_job_count(cat.get("attributes")) or 0
        price = cat.get("posterRateDisplay") or ""
        services.append({
            "name": site_name,
            "count": count,
            "price": price,
            "blurb": SERVICE_BLURBS.get(site_name, ""),
            "_category_id": cat.get("id"),
            "_tr_name": cat.get("name"),
        })

    # Keep STATIC order; drop empty/unknown
    order = [s["name"] for s in STATIC["services"]]
    services.sort(key=lambda s: order.index(s["name"]) if s["name"] in order else 99)

    return {
        "name": page.get("displayName") or STATIC["name"],
        "rating": (rating.get("average") or "5.0").strip(),
        "reviews": reviews,
        "tasks": int(page.get("taskCount") or 0),
        "location": f"{metro}, WA",
        "since": since,
        "vehicles": vehicles,
        "avatar": page.get("avatarUrl") or STATIC["avatar"],
        "profile_url": PROFILE_URL,
        "bio": page.get("description") or STATIC["bio"],
        "tasker_id": page.get("id"),
        "photos": photos,
        "services": services,
        "categories": [
            {
                "id": c.get("id"),
                "name": c.get("name"),
                "review_count": int(
                    re.search(r"(\d+)", (c.get("rating") or {}).get("totalReviews") or "0").group(1)
                )
                if re.search(r"(\d+)", (c.get("rating") or {}).get("totalReviews") or "")
                else 0,
            }
            for c in (page.get("categories") or [])
        ],
    }


def fetch_reviews(session: requests.Session, tasker_id: int, categories: list) -> list:
    """Pull written reviews for every category that has them via tRPC."""
    out = []
    seen = set()
    for cat in categories:
        if not cat.get("id") or cat.get("review_count", 0) < 1:
            continue
        page = 1
        total_pages = 1
        while page <= total_pages:
            payload = {
                "json": {
                    "categoryId": cat["id"],
                    "locale": "en-US",
                    "page": page,
                    "taskerId": tasker_id,
                }
            }
            url = (
                TRPC_REVIEWS
                + "?input="
                + urllib.parse.quote(json.dumps(payload, separators=(",", ":")))
            )
            r = session.get(url, timeout=45)
            r.raise_for_status()
            body = r.json()
            bff = (((body.get("result") or {}).get("data") or {}).get("json") or {}).get("bff") or {}
            total_pages = int(bff.get("totalPages") or 1)
            for rev in bff.get("reviews") or []:
                rid = rev.get("id")
                if rid in seen:
                    continue
                seen.add(rid)
                msg = (rev.get("message") or "").strip()
                poster = rev.get("poster") or {}
                out.append({
                    "id": rid,
                    "n": poster.get("displayName") or "Client",
                    "c": cat["name"],
                    "t": msg,
                    "rating": rev.get("displayRating") or 5,
                    "createdAt": rev.get("createdAt"),
                })
            page += 1

    # Newest first; prefer reviews with written text for the homepage carousel
    out.sort(key=lambda r: r.get("createdAt") or 0, reverse=True)
    return out


def download_gallery(session: requests.Session, photos: list, dry: bool) -> tuple[list[str], list[str]]:
    """Download newest photos into public/gallery/. Returns (paths, new_paths)."""
    GALLERY_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    new_paths = []
    for photo in photos[:MAX_GALLERY]:
        dest = GALLERY_DIR / f"tr-{photo['id']}.jpg"
        rel = f"public/gallery/{dest.name}"
        if not dest.exists():
            if dry:
                log(f"DRY would download photo {photo['id']} ({photo['category']})")
            else:
                log(f"Downloading gallery image {photo['id']} ({photo['category']})")
                rr = session.get(photo["url"], timeout=60)
                rr.raise_for_status()
                dest.write_bytes(rr.content)
                new_paths.append(rel)
        paths.append(rel)
    return paths, new_paths


def load_old() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            log("WARN: existing JSON unreadable, treating as empty")
    return {}


def summarize(d: dict) -> dict:
    review_ids = sorted(r.get("id") for r in (d.get("testimonials") or []) if r.get("id"))
    gallery = list(d.get("gallery") or [])
    return {
        "rating": d.get("rating"),
        "reviews": d.get("reviews"),
        "tasks": d.get("tasks"),
        "location": d.get("location"),
        "since": d.get("since"),
        "vehicles": d.get("vehicles"),
        "review_ids": review_ids,
        "gallery": gallery,
    }


def diff(old: dict, new: dict) -> list:
    changes = []
    for k in ("rating", "reviews", "tasks", "location", "since", "vehicles"):
        ov, nv = old.get(k), new.get(k)
        if ov != nv:
            changes.append((k, ov, nv))

    old_ids = set(old.get("review_ids") or [])
    new_ids = set(new.get("review_ids") or [])
    added_reviews = sorted(new_ids - old_ids)
    removed_reviews = sorted(old_ids - new_ids)
    if added_reviews:
        changes.append(("testimonials_added", None, len(added_reviews)))
    if removed_reviews:
        changes.append(("testimonials_removed", None, len(removed_reviews)))

    old_g = set(old.get("gallery") or [])
    new_g = set(new.get("gallery") or [])
    added_g = sorted(new_g - old_g)
    if added_g:
        changes.append(("gallery_added", None, added_g))
    removed_g = sorted(old_g - new_g)
    if removed_g:
        changes.append(("gallery_removed", None, removed_g))
    return changes


def build_record(live: dict, gallery: list[str], testimonials: list) -> dict:
    # Preserve travelFee from prior JSON when present
    old = load_old()
    travel = old.get("travelFee") or STATIC["travelFee"]

    services = []
    for s in live.get("services") or []:
        services.append({
            "name": s["name"],
            "count": s["count"],
            "price": s["price"],
            "blurb": s.get("blurb") or "",
        })
    if not services:
        services = list(STATIC["services"])

    # Homepage shows written reviews first, then silent 5-stars as fallback
    written = [t for t in testimonials if t.get("t")]
    silent = [t for t in testimonials if not t.get("t")]
    ordered = written + silent

    return {
        "name": live.get("name") or STATIC["name"],
        "bio": live.get("bio") or STATIC["bio"],
        "services": services,
        "gallery": gallery,
        "avatar": live.get("avatar") or STATIC["avatar"],
        "rating": live["rating"],
        "reviews": live["reviews"],
        "tasks": live["tasks"],
        "location": live["location"],
        "since": live["since"],
        "vehicles": live["vehicles"],
        "profile_url": PROFILE_URL,
        "travelFee": travel,
        "testimonials": [
            {
                "id": t["id"],
                "n": t["n"],
                "c": t["c"],
                "t": t["t"] or "Left a 5-star rating.",
                "rating": t.get("rating", 5),
                "createdAt": t.get("createdAt"),
            }
            for t in ordered
        ],
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def append_changelog(changes, record) -> None:
    entry = {
        "ts": record["last_updated"],
        "changes": [{"field": c[0], "from": c[1], "to": c[2]} for c in changes],
    }
    history = []
    if CHANGELOG.exists():
        try:
            history = json.loads(CHANGELOG.read_text())
        except Exception:
            history = []
    history.append(entry)
    CHANGELOG.write_text(json.dumps(history[-100:], indent=2) + "\n")


def push() -> None:
    import subprocess
    log("Committing + pushing to origin...")
    subprocess.run(["git", "-C", str(ROOT), "add", "-A"], check=True)
    msg = f"auto: profile sync {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    subprocess.run(["git", "-C", str(ROOT), "commit", "-m", msg], check=True)
    subprocess.run(["git", "-C", str(ROOT), "push"], check=True)
    log("Pushed.")


def main() -> None:
    dry = "--dry" in sys.argv
    do_push = "--push" in sys.argv
    session = _session()

    try:
        live = scrape_profile(session)
    except Exception as e:
        log(f"ERROR scraping profile: {e}")
        sys.exit(2)

    log(
        f"Live profile: {live['reviews']} reviews, {live['tasks']} tasks, "
        f"{len(live['photos'])} photos"
    )

    try:
        testimonials = fetch_reviews(session, live["tasker_id"], live["categories"])
    except Exception as e:
        log(f"ERROR fetching reviews: {e}")
        sys.exit(2)
    written = sum(1 for t in testimonials if t.get("t"))
    log(f"Fetched {len(testimonials)} reviews ({written} with text)")

    try:
        gallery, new_images = download_gallery(session, live["photos"], dry=dry)
    except Exception as e:
        log(f"ERROR downloading gallery: {e}")
        sys.exit(2)
    if new_images:
        log(f"New gallery images: {len(new_images)}")

    record = build_record(live, gallery, testimonials)
    old = load_old()
    changes = diff(summarize(old), summarize(record))

    if changes:
        for f, o, n in changes:
            log(f"CHANGE {f}: {o!r} -> {n!r}")
    else:
        log("No changes detected.")

    if dry:
        log("Dry run — not writing.")
        return

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(record, indent=2) + "\n")
    log(f"Wrote {DATA_FILE.name}")

    if changes:
        append_changelog(changes, record)
        log(f"Logged {len(changes)} change(s) to changelog.")

    if do_push and changes:
        try:
            push()
        except Exception as e:
            log(f"ERROR pushing: {e}")
            sys.exit(3)
    elif do_push and not changes:
        log("No changes — skipping push.")

    log("Done.")


if __name__ == "__main__":
    main()
