# Service-Generated Lead Website Patterns

## Auto-Update Lead Generation Websites

Pattern for creating lead-generation websites that auto-update from public profiles (Taskrabbit, Thumbtack, Yelp, etc.).

### Architecture
```
save3vinny-leadgen/
├── index.html           # Dynamic website (fetches JSON at runtime)
├── data/
│   └── profile-stats.json  # Scrape target - updated daily
├── scraper.py           # Python script: fetches profile → updates JSON
└── README.md            # Documentation
```

### Key Features

1. **Dynamic Content Loading**
   - Website fetches `data/profile-stats.json` at runtime
   - Stats (ratings, review count, task count) display automatically
   - Service cards generated from JSON data

2. **Daily Auto-Updates**
   - Deploy cron job to run scraper daily
   - JSON file updates, website reflects changes automatically
   - Fallback to cached data if scraper fails

3. **XSS-Safe Implementation**
   ```javascript
   // Use textContent for safe dynamic content
   el.textContent = data.value;
   
   // Helper function to escape HTML
   function escapeHtml(text) {
       const div = document.createElement('div');
       div.textContent = String(text);
       return div.innerHTML;
   }
   ```

### Technical Implementation

**HTML Structure:**
```html
<div id="stat-tasks" class="stat-number">--</div>
<div id="stat-reviews" class="stat-number">--</div>
<div id="services-container" class="services"></div>
```

**JavaScript Pattern:**
```javascript
async function fetchProfileData() {
    const response = await fetch('data/profile-stats.json');
    const data = await response.json();
    updateWebsite(data);
}

function updateWebsite(data) {
    document.getElementById('stat-tasks').textContent = data.tasks + '+';
    // ... more updates
}
```

### Deployment Notes

- Works with static hosting (Netlify, Vercel, GitHub Pages)
- No server-side code needed
- JSON file served as static asset
- Update via cron or CI/CD pipeline

### File Locations

- Website: `/Users/MykeyToft/booking-pages-local/save3vinny-leadgen/`
- Data: `data/profile-stats.json`
- Scraper: `scraper.py`

### Related Patterns

- Taskrabbit profile scraping: Extract rating, review count, service categories, task history
- Dynamic form prefilling from profile data
- Testimonial carousel from latest reviews