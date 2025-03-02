"""
Utility functions for the Indeed.de job scraper.
"""
import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_config():
    """
    Load configuration from environment variables.
    """
    # clean values from comments
    def clean_value(value):
        # check if value is a string and not empty
        if value and isinstance(value, str):
            # Remove any comments (starting with #)
            # split by # and take the first part 
            if '#' in value:
                value = value.split('#')[0].strip()
        return value
    
    config = {
        'job_title': os.getenv('JOB_TITLE', 'software engineer'),
        'location': os.getenv('LOCATION', 'Berlin'),
        'radius': int(clean_value(os.getenv('RADIUS', '25'))),
        'results_per_page': int(clean_value(os.getenv('RESULTS_PER_PAGE', '15'))),
        'max_pages': int(clean_value(os.getenv('MAX_PAGES', '5'))),
        'output_csv': clean_value(os.getenv('OUTPUT_CSV', 'True')).lower() == 'true',
        'output_json': clean_value(os.getenv('OUTPUT_JSON', 'True')).lower() == 'true',
        'headless': clean_value(os.getenv('HEADLESS', 'False')).lower() == 'true',
        'timeout': int(clean_value(os.getenv('TIMEOUT', '10')))
    }
    return config


## used this approach to filter the results instead of interacting with the website
def build_indeed_url(job_title, location, radius, start=0, limit=15):
    """
    Build the Indeed.de search URL with the given parameters.
    
    Args:
        job_title (str): Job title to search for
        location (str): Location to search in
        radius (int): Search radius in km
        start (int): Starting position for pagination
        limit (int): Number of results per page
        
    Returns:
        str: The search URL
    """
    # Format job title and location for URL
    job_title = job_title.replace(' ', '+')
    location = location.replace(' ', '+')
    
    # Build URL
    url = f"https://de.indeed.com/jobs?q={job_title}&l={location}&radius={radius}&limit={limit}"
    
    # Add pagination if needed
    if start > 0:
        url += f"&start={start}"
        
    return url

def save_to_csv(data, filename=None):
    """
    Save job data to a CSV file.
    
    Args:
        data (list): List of job dictionaries
        filename (str, optional): Output filename. If None, a default name will be used.
    
    Returns:
        str: Path to the saved file
    """
    if not data:
        print("No data to save to CSV.")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"indeed_jobs_{timestamp}.csv"
    
    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save to CSV
    output_path = output_dir / filename
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Data saved to {output_path}")
    
    return str(output_path)

def save_to_json(data, filename=None):
    """
    Save job data to a JSON file.
    
    Args:
        data (list): List of job dictionaries
        filename (str, optional): Output filename. If None, a default name will be used.
    
    Returns:
        str: Path to the saved file
    """
    if not data:
        print("No data to save to JSON.")
        return None
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"indeed_jobs_{timestamp}.json"
    
    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save to JSON
    output_path = output_dir / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {output_path}")
    
    return str(output_path) 