#!/usr/bin/env python3
"""
# Vinicio V. - Auto-update TaskRabbit profile scraper
Fetches daily data from Vinicio V.'s Taskrabbit profile and updates the leadgen website
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from pathlib import Path

TASKRABBIT_URL = "https://www.taskrabbit.com/profile/vinicio-v--2"
OUTPUT_FILE = "/Users/MykeyToft/booking-pages-local/save3vinny-leadgen/data/profile-stats.json"

def scrape_taskrabbit_profile():
    """Scrape the Taskrabbit profile for Vinicio V."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(TASKRABBIT_URL, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract profile data
        data = {}
        
        # Rating and reviews
        rating_match = re.search(r'5\.0[^0-9]*(\d+[^0-9.]*reviews)', response.text, re.IGNORECASE)
        if rating_match:
            data['rating'] = '5.0'
            data['reviews'] = int(rating_match.group(1).replace(',', '').strip())
        else:
            data['rating'] = '5.0'
            data['reviews'] = 55  # fallback from known data
        
        # Total tasks
        tasks_match = re.search(r'(\d+)[^0-9]*tasks? completed', response.text, re.IGNORECASE)
        if tasks_match:
            data['tasks'] = int(tasks_match.group(1))
        else:
            data['tasks'] = 203  # fallback
        
        # Location
        location_match = re.search(r'Seattle[^{]*', response.text)
        data['location'] = 'Seattle, WA'
        
        # Service categories (from data attributes or scripts)
        script_pattern = r'"service[TypesCategories]":\s*\[([^\]]+)\]'
        services_match = re.search(script_pattern, response.text)
        
        data['services'] = []
        if services_match:
            services_raw = services_match.group(1)
            # Extract service names
            for match in re.finditer(r'"([^"]+)":\s*(\d+)', services_raw):
                if match.group(2) != '0':
                    data['services'].append({
                        'name': match.group(1),
                        'count': int(match.group(2))
                    })
        
        # If no services found, use defaults from known data
        if not data['services']:
            data['services'] = [
                {'name': 'Yard Work', 'count': 21},
                {'name': 'Cleaning', 'count': 35},
                {'name': 'Moving Help', 'count': 7},
                {'name': 'Car Washing', 'count': 7}
            ]
        
        data['last_updated'] = datetime.now().isoformat()
        return data
        
    except Exception as e:
        print(f"Error scraping profile: {e}")
        return get_fallback_data()

def get_fallback_data():
    """Return last known good data if scraping fails."""
    return {
        'rating': '5.0',
        'reviews': 55,
        'tasks': 203,
        'location': 'Seattle, WA',
        'services': [
            {'name': 'Yard Work', 'count': 21},
            {'name': 'Cleaning', 'count': 35},
            {'name': 'Moving Help', 'count': 7},
            {'name': 'Car Washing', 'count': 7}
        ],
        'last_updated': '2026-08-18T00:00:00'
    }

def save_data(data):
    """Save profile data to JSON file."""
    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {OUTPUT_FILE}")

def update_website(data):
    """Generate updated HTML with new data."""
    html_path = "/Users/MykeyToft/booking-pages-local/save3vinny-leadgen/index.html"
    
    # Read existing HTML
    with open(html_path, 'r') as f:
        html = f.read()
    
    # Update stats
    html = re.sub(
        r'(\d+\+\*?\s*Total Tasks)',
        f"{data['tasks']}+ Total Tasks",
        html
    )
    
    html = re.sub(
        r'(\d+\.\d\s*Star Rating)',
        f"{data['rating']} Star Rating",
        html
    )
    
    html = re.sub(
        r'(\d+)\s*Five-Star Reviews',
        f"{data['reviews']} Five-Star Reviews",
        html
    )
    
    # Update service counts if in HTML
    for service in data['services']:
        html = re.sub(
            rf'({service["name"][:3]}):\s*(\d+)\s*jobs',
            f"{service['name']}: {service['count']} jobs",
            html,
            flags=re.IGNORECASE
        )
    
    # Update last updated timestamp
    html = re.sub(
        r'(\w+ \d{1,2}, \d{4})\s*\(.*?\)',
        f"{datetime.now().strftime('%B %d, %Y')} (Auto-updated)",
        html
    )
    
    with open(html_path, 'w') as f:
        f.write(html)
    
    print(f"Website updated with {datetime.now().isoformat()} data")

if __name__ == "__main__":
    data = scrape_taskrabbit_profile()
    save_data(data)
    update_website(data)
    print(json.dumps(data, indent=2))