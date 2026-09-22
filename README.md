# Vinicio V. — Professional Services Lead Generation

**Target:** Vinicio V. - transitioning from TaskRabbit to independent client business

## Overview

A professional lead-generation website with two booking pathways:
1. **TaskRabbit** - For standard services with fixed pricing
2. **Custom Quote** - For services outside TaskRabbit scope

The site auto-updates daily from Vinicio's public TaskRabbit profile: review count, task count, rates, written testimonials, and work photos.

## Files

```
vinicio-v/
├── index.html                 # Business website (reads JSON at runtime)
├── data/
│   ├── profile-stats.json     # Live stats, testimonials, gallery paths
│   └── changelog.json         # Sync history
├── public/gallery/            # Downloaded TaskRabbit work photos
├── monitor.py                 # Daily scraper (stats + reviews + images)
├── .github/workflows/
│   └── daily-taskrabbit-sync.yml
└── README.md
```

## Daily auto-update

GitHub Actions runs `monitor.py` every day at 14:00 UTC and commits any changes:

- Profile stats (rating, reviews, tasks, rates)
- New written reviews → `data/profile-stats.json` → `testimonials`
- New work photos → `public/gallery/tr-*.jpg` → `gallery`

Manual sync:

```bash
pip install -r requirements.txt
python3 monitor.py          # update locally
python3 monitor.py --dry    # fetch + diff only
python3 monitor.py --push   # update + commit + push
```

You can also trigger **Daily TaskRabbit sync** from the Actions tab (`workflow_dispatch`).

## Booking Flow

### 1. TaskRabbit Booking (Default)
- Link: `taskrabbit.com/profile/vinicio-v--2`
- Standard services: Yard Work, Cleaning, Moving, Car Wash
- Fixed hourly rates (live rates come from the daily sync)

### 2. Custom Quote Form
Captures leads for:
- Services not on TaskRabbit
- Custom project requirements
- Price negotiations

**Submits to:** `berlinsofio80@gmail.com` via Formspree

## Customization

### Form Endpoint
Change the FORM_ENDPOINT variable in the `<script>` section to point to your preferred form service (Formspree, Netlify Forms, Getform, etc.)

### Email Notifications
Quote requests are sent to `berlinsofio80@gmail.com` through the Formspree form on the quote form in `index.html`.

### Services
Service blurbs live in `monitor.py` (`STATIC` / `SERVICE_BLURBS`). Counts and prices refresh from TaskRabbit.

## Deployment

1. Upload `index.html`, `data/`, and `public/` to your host (or use GitHub Pages)
2. Keep the daily Actions workflow enabled so reviews and images stay current
3. Form submissions email to the configured address

### Recommended Hosts
- Netlify (built-in form handling)
- Vercel (requires form backend)
- GitHub Pages + Formspree
- Any static host with POST capability
