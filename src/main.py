#!/usr/bin/env python3
"""
Main entry point for the Indeed.de manual job scraper.
"""
import time
import logging
import argparse
from pathlib import Path
from manual_scraper import ManualIndeedScraper
from utils import get_config, build_indeed_url, save_to_csv, save_to_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Manually scrape job listings from Indeed.de')
    
    parser.add_argument('--job-title', type=str, help='Job title to search for')
    parser.add_argument('--location', type=str, help='Location to search in')
    parser.add_argument('--radius', type=int, help='Search radius in km')
    parser.add_argument('--max-pages', type=int, help='Maximum number of pages to scrape')
    parser.add_argument('--output-csv', action='store_true', help='Save results to CSV')
    parser.add_argument('--output-json', action='store_true', help='Save results to JSON')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--no-headless', dest='headless', action='store_false', help='Run browser in visible mode')
    
    return parser.parse_args()

def main():
    """
    Main function to run the manual scraper.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Load configuration from .env file
    config = get_config()
    
    # Override config with command line arguments if provided
    if args.job_title:
        config['job_title'] = args.job_title
    if args.location:
        config['location'] = args.location
    if args.radius:
        config['radius'] = args.radius
    if args.max_pages:
        config['max_pages'] = args.max_pages
    if args.output_csv:
        config['output_csv'] = True
    if args.output_json:
        config['output_json'] = True
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Print configuration
    logger.info("Running with the following configuration:")
    logger.info(f"Job Title: {config['job_title']}")
    logger.info(f"Location: {config['location']}")
    logger.info(f"Radius: {config['radius']} km")
    logger.info(f"Max Pages: {config['max_pages']}")
    
    # Build URL
    url = build_indeed_url(
        config['job_title'],
        config['location'],
        config['radius'],
        limit=config['results_per_page']
    )
    
    # Initialize scraper
    with ManualIndeedScraper(timeout=config['timeout']) as scraper:
        # Manual navigation
        if not scraper.manual_navigate(url):
            logger.info("Manual navigation aborted.")
            return
        
        # Extract job listings
        all_jobs = []
        current_page = 0
        
        while current_page < config['max_pages']:
            # Extract job listings
            jobs = scraper.extract_job_listings()
            logger.info(f"Extracted {len(jobs)} jobs from page {current_page + 1}")
            
            if not jobs:
                logger.warning(f"No jobs found on page {current_page + 1}. Stopping.")
                break
            
            # Add jobs to the list
            all_jobs.extend(jobs)
            
            # Check if there's a next page
            if not scraper.has_next_page():
                logger.info("No more pages available.")
                break
            
            # Go to the next page
            if not scraper.go_to_next_page():
                logger.error(f"Failed to navigate to page {current_page + 2}. Stopping.")
                break
            
            current_page += 1
            
            # Sleep to avoid being blocked
            time.sleep(3)
        
        # Save results
        logger.info(f"Scraped a total of {len(all_jobs)} jobs")
        
        if config['output_csv']:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"indeed_jobs_{config['job_title'].replace(' ', '_')}_{config['location'].replace(' ', '_')}_{timestamp}.csv"
            save_to_csv(all_jobs, filename)
        
        if config['output_json']:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"indeed_jobs_{config['job_title'].replace(' ', '_')}_{config['location'].replace(' ', '_')}_{timestamp}.json"
            save_to_json(all_jobs, filename)

if __name__ == "__main__":
    main() 