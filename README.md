# Vinicio V. — Professional Services Lead Generation

**Target:** Vinicio V. - transitioning from TaskRabbit to independent client business

## Overview

A professional lead-generation website with two booking pathways:
1. **TaskRabbit** - For standard services with fixed pricing
2. **Custom Quote** - For services outside TaskRabbit scope

## Files

```
vinicio-v-services/
├── index.html          # Business website with email form
├── data/profile-stats.json  # Auto-updating profile data
├── scraper.py          # Daily profile scraper
└── README.md
```

## Booking Flow

### 1. TaskRabbit Booking (Default)
- Link: `taskrabbit.com/profile/vinicio-v--2`
- Standard services: Yard Work, Cleaning, Moving, Car Wash
- Fixed hourly rates ($41 - $50/hr)

### 2. Custom Quote Form
Captures leads for:
- Services not on TaskRabbit
- Custom project requirements
- Price negotiations

**Submits to:** `berlinsofio80@gmail.com` via Formspree

## Real Taskrabbit Data

| Service | Jobs | Rate |
|---------|------|------|
| Yard Work | 21 | $41.29/hr |
| Cleaning | 35 | $47.49/hr |
| Moving Help | 13 | $43.33/hr |
| Car Washing | 7 | $49.55/hr |
| Estate Cleanout | 5 | $50/hr |
| Laundry Service | 1 | $32/hr |

**Total:** 214+ tasks completed | 55 reviews | 5.0★ rating

## Customization

### Form Endpoint
Change the FORM_ENDPOINT variable in the `<script>` section to point to your preferred form service (Formspree, Netlify Forms, Getform, etc.)

### Email Notifications
Currently configured to send to `berlinsofio80@gmail.com`. Update the `_to` field as needed.

### Services
Update services in `data/profile-stats.json` or modify the HTML structure.

## Deployment

1. Upload `index.html` and `data/` folder to your host
2. Enable JavaScript support
3. Form submissions will email to configured address

### Recommended Hosts
- Netlify (built-in form handling)
- Vercel (requires form backend)
- GitHub Pages + Formspree
- Any static host with POST capability