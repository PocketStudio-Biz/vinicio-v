#!/usr/bin/env python3
"""
Vinicio V. — TaskRabbit monitor bot
===================================
Scrapes Vinicio's public TaskRabbit profile, diffs it against the last-known
snapshot in data/profile-stats.json, and — when anything changed — rewrites the
JSON. The website (index.html) reads that JSON at runtime, so updating the file
*is* updating the page.

Run:
    python3 monitor.py            # update locally, print a report
    python3 monitor.py --push     # also git commit + push (deploy)
    python3 monitor.py --dry      # fetch + diff only, never write

Exit code 0 = ran (whether or not data changed). Non-zero = hard failure.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

PROFILE_URL = "https://www.taskrabbit.com/profile/vinicio-v--2"
ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "profile-stats.json"
CHANGELOG = ROOT / "data" / "changelog.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Known-good dataset. Live numbers (rating/reviews/tasks/location/since) are
# refreshed by the scraper; services + bio are stable and only overwritten if
# the scrape explicitly returns them.
STATIC = {
    "name": "Vinicio V.",
    "bio": (
        "Part-time Tasker helping pay off student loans — and genuinely "
        "enjoying the work. Integrity and hard work come first. Two-hour "
        "minimum on most tasks."
    ),
    "services": [
        {"name": "Yard Work", "count": 21, "price": "$41.29/hr",
         "blurb": "Mowing, edging, planting, clean-up and landscaping."},
        {"name": "Cleaning", "count": 35, "price": "$47.49/hr",
         "blurb": "Deep cleans, move-in/out, organizing — detail-obsessed."},
        {"name": "Moving Help", "count": 13, "price": "$43.33/hr",
         "blurb": "Loading, unloading, in-home moves, furniture."},
        {"name": "Car Washing", "count": 7, "price": "$49.55/hr",
         "blurb": "Interior + exterior detailing at your place."},
        {"name": "Estate Cleanout", "count": 5, "price": "$50/hr",
         "blurb": "Whole-home clear-outs, sorting, removal."},
        {"name": "Laundry Service", "count": 1, "price": "$32/hr",
         "blurb": "Wash, fold, and closet organization."},
    ],
    "gallery": [
        "public/gallery/yard1.jpg",
        "public/gallery/yard2.jpg",
        "public/gallery/yard3.jpg",
        "public/gallery/yard4.jpg",
        "public/gallery/yard5_large.jpg",
        "public/gallery/yard6.jpg",
    ],
    "avatar": "public/profile.jpg",
}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def scrape():
    """Return a dict of live profile fields, or raise on failure."""
    r = requests.get(PROFILE_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    html = r.text

    blob = re.search(
        r'"displayName":"(.*?)".*?'
        r'"metroName":"(.*?)".*?'
        r'"rating":\{"average":"(.*?)","totalReviews":"\((\d+)\s+reviews\)"[^}]*\}.*?'
        r'"slug":"(.*?)".*?'
        r'"taskCount":(\d+).*?'
        r'"vehiclesDisplay":"(.*?)"',
        html, re.S)
    if not blob:
        raise ValueError("Could not locate the profile data blob in HTML")

    name, metro, avg, reviews, slug, tasks, vehicles = blob.groups()

    since_m = re.search(r"Tasker since (\d{4})", html)
    since = int(since_m.group(1)) if since_m else None

    avatar_m = re.search(r'<img alt="Vinicio V\." src="(https://[^"]+)"', html)
    avatar = avatar_m.group(1) if avatar_m else STATIC["avatar"]

    return {
        "name": name or STATIC["name"],
        "rating": avg.strip(),
        "reviews": int(reviews),
        "tasks": int(tasks),
        "location": f"{metro}, WA" if metro else "Seattle, WA",
        "since": since,
        "vehicles": vehicles.replace("Vehicles: ", "").strip(),
        "avatar": avatar,
        "profile_url": PROFILE_URL,
    }


def load_old():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            log("WARN: existing JSON unreadable, treating as empty")
    return {}


def summarize(d):
    return {
        "rating": d.get("rating"),
        "reviews": d.get("reviews"),
        "tasks": d.get("tasks"),
        "location": d.get("location"),
        "since": d.get("since"),
        "vehicles": d.get("vehicles"),
    }


def diff(old, new):
    changes = []
    for k in ("rating", "reviews", "tasks", "location", "since", "vehicles"):
        ov, nv = old.get(k), new.get(k)
        if ov != nv:
            changes.append((k, ov, nv))
    return changes


def build_record(live):
    rec = dict(STATIC)
    rec.update({
        "rating": live["rating"],
        "reviews": live["reviews"],
        "tasks": live["tasks"],
        "location": live["location"],
        "since": live["since"],
        "vehicles": live["vehicles"],
        "avatar": live["avatar"],
        "profile_url": PROFILE_URL,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    })
    return rec


def append_changelog(changes, record):
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
    # keep last 100 entries
    CHANGELOG.write_text(json.dumps(history[-100:], indent=2))


def push():
    import subprocess
    log("Committing + pushing to origin...")
    subprocess.run(["git", "-C", str(ROOT), "add", "-A"], check=True)
    msg = f"auto: profile sync {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    subprocess.run(["git", "-C", str(ROOT), "commit", "-m", msg], check=True)
    subprocess.run(["git", "-C", str(ROOT), "push"], check=True)
    log("Pushed.")


def main():
    dry = "--dry" in sys.argv
    do_push = "--push" in sys.argv

    try:
        live = scrape()
    except Exception as e:
        log(f"ERROR scraping profile: {e}")
        sys.exit(2)

    old = load_old()
    new_summary = summarize(live)
    old_summary = summarize(old)
    changes = diff(old_summary, new_summary)

    if changes:
        for f, o, n in changes:
            log(f"CHANGE {f}: {o!r} -> {n!r}")
    else:
        log("No changes detected.")

    if dry:
        log("Dry run — not writing.")
        return

    record = build_record(live)
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
