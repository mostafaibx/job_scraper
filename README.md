# Job Scraper

A web scraping tool built with Python and Selenium to extract job listings from Indeed.de. This scraper is designed to handle Cloudflare protection and cookie consent dialogs.

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Configure your search parameters in the `.env` file:

```
# Indeed.de Scraper Configuration

# Search Parameters
JOB_TITLE=software engineer
LOCATION=Berlin
RADIUS=25
RESULTS_PER_PAGE=15
MAX_PAGES=5

# Output Settings
OUTPUT_CSV=True
OUTPUT_JSON=True

# Browser Settings
TIMEOUT=30
```

## Usage

### Manual Scraper

The manual scraper is designed to handle Cloudflare protection and cookie consent dialogs effectively:

```
python scrape.py
```

or

```
python src/main.py
```

When using the scraper:
1. A browser window will open
2. The scraper will try to navigate automatically using saved cookies if available
3. If a CAPTCHA or Cloudflare challenge appears, you'll be prompted to solve it manually
4. Once you've solved the challenge, type 'done' to continue scraping or 'save' to save cookies for future use
5. The scraper will extract job listings and handle pagination

### Cookie Management

The scraper saves cookies to `indeed_cookies.pkl` after successful navigation. These cookies are loaded automatically on subsequent runs, which helps avoid having to solve CAPTCHAs repeatedly. If valid cookies are found and no challenges are detected, the scraper will proceed automatically without prompting.

### Command-line Arguments

You can also use command-line arguments for more configuration options:

```
python src/main.py --job-title "Data Scientist" --location "Munich" --radius 30 --max-pages 3
```

## Features

- Extracts job titles, companies, locations, salaries, and descriptions
- Handles pagination to scrape multiple pages of results
- Configurable search parameters (job title, location, etc.)
- Export data to CSV and JSON formats
- Handles Cloudflare protection and cookie consent dialogs
- Saves and loads cookies to avoid repeated CAPTCHA solving
- Automatic navigation when possible, with manual fallback when needed

## Output

The scraped data is saved in the `output` directory in both CSV and JSON formats:
- `output/indeed_jobs_[job_title]_[location]_[timestamp].csv`
- `output/indeed_jobs_[job_title]_[location]_[timestamp].json`

## Project Structure

```
├── .env                  # Environment variables and configuration
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── scrape.py             # Default entry point (runs manual scraper)
├── src/                  # Source code
│   ├── __init__.py       # Package initialization
│   ├── main.py           # Manual scraper entry point
│   ├── manual_scraper.py # Manual scraper for handling Cloudflare protection
│   └── utils.py          # Utility functions
├── output/               # Scraped data output
├── examples/             # Example scripts
│   └── simple_search.py  # Simple search example
└── tests/                # Test files
    ├── __init__.py       # Test package initialization
    └── test_utils.py     # Utility function tests
```

## Handling Anti-Scraping Measures

Indeed.de employs several anti-scraping measures:

1. **Cloudflare Protection**: The scraper attempts to bypass this using cookies, but will prompt you to solve CAPTCHA challenges interactively if needed.
2. **Cookie Consent Dialogs**: The scraper attempts to automatically handle these, with manual fallback if needed.
3. **Rate Limiting**: The scraper includes delays between requests to avoid being blocked.

## Troubleshooting

- **Cloudflare Challenges**: Solve the CAPTCHA when prompted and consider saving cookies with the 'save' command.
- **Cookie Consent Issues**: The scraper will prompt you to handle these manually if automatic handling fails.
- **No Results**: Make sure your browser window is visible to solve any challenges.
- **Blocked Access**: Delete the cookies file and try again with a different IP address or wait before retrying.

## License

MIT 