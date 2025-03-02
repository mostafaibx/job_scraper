#!/usr/bin/env python3
"""
Simple example of using the Indeed.de manual job scraper.
"""
import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.manual_scraper import ManualIndeedScraper
from src.utils import build_indeed_url, save_to_csv, save_to_json

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Simple Indeed.de job search example")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    return parser.parse_args()

def main():
    """
    Run a simple job search and save the results.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Search parameters
    job_title = "Python Developer"
    location = "Berlin"
    radius = 25
    
    # Build URL
    url = build_indeed_url(job_title, location, radius)
    print(f"Searching for '{job_title}' in '{location}' (radius: {radius}km)")
    print(f"URL: {url}")
    print(f"Headless Mode: {'Yes' if args.headless else 'No'}")
    
    # Initialize scraper
    with ManualIndeedScraper(timeout=15, headless=args.headless) as scraper:
        # Manual navigation
        print("\nNavigating to the job search page...")
        print("If a CAPTCHA or Cloudflare challenge appears, you'll be prompted to solve it.")
        print("Otherwise, the scraper will proceed automatically if it can access the job listings.\n")
        
        if not scraper.manual_navigate(url):
            print("Navigation aborted")
            return
        
        # Extract job listings
        jobs = scraper.extract_job_listings()
        print(f"Found {len(jobs)} jobs")
        
        if jobs:
            # Save results
            csv_path = save_to_csv(jobs)
            json_path = save_to_json(jobs)
            
            print(f"Results saved to:")
            print(f"- CSV: {csv_path}")
            print(f"- JSON: {json_path}")

if __name__ == "__main__":
    # Create examples directory if it doesn't exist
    Path(Path(__file__).parent).mkdir(exist_ok=True)
    
    main() 