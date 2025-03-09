# Indeed Job Scraper

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.29.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A web scraping solution built with Python and Selenium that extracts job listings from Indeed.de while handling anti-scraping measures including Cloudflare protection and cookie consent dialogs.

## 🚀 Features

- **Anti-Scraping Handling**: bypasses Cloudflare protection and cookie consent dialogs
- **Cookie Management**: Saves and reuses cookies to minimize Cloudflare windows
- **Data Extraction**: Captures job titles, companies, locations, salaries, and full descriptions
- **Configurable Search Parameters**: Easily customize job title, location, search radius, and more
- **Multiple Export Formats**: Save data in both CSV and JSON formats
- **Pagination Support**: Automatically navigates through multiple pages of results
- **Configurable via Environment Variables**: Easy setup through .env file or command-line arguments

## 🛠️ Technical Implementation

This project demonstrates several advanced programming concepts:

- **Web Automation**: Using Selenium WebDriver for browser control and interaction
- **Anti-Bot Measure Handling**: Techniques to bypass sophisticated protection systems
- **Object-Oriented Design**: Clean, modular code structure with proper class abstractions
- **Context Managers**: Implementation of Python's `with` statement protocol
- **Command-Line Interface**: Flexible CLI with argparse for parameter configuration
- **Environment Configuration**: Using dotenv for configuration management
- **Data Processing**: Structured extraction and transformation of web data
- **File I/O Operations**: Saving and loading data in multiple formats

## 📋 Prerequisites

- Python 3.9 or higher
- Chrome browser installed

## 🔧 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/indeed-job-scraper.git
   cd indeed-job-scraper
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Configure your search parameters in the `.env` file:

```ini
# Indeed.de Scraper Configuration

# Search Parameters
JOB_TITLE=Working student
LOCATION=Germany
RADIUS=25
RESULTS_PER_PAGE=15
MAX_PAGES=5

# Output Settings
OUTPUT_CSV=True
OUTPUT_JSON=True

# Browser Settings
TIMEOUT=30
```

## 🚀 Usage

### Basic Usage

Run the scraper with default settings from the .env file:

```bash
python scrape.py
```

or

```bash
python src/main.py
```

### Command-line Arguments

Override configuration with command-line arguments:

```bash
python src/main.py --job-title "Data Scientist" --location "Munich" --radius 30 --max-pages 3
```

### Interactive Mode

When using the scraper:

1. A Chrome browser window will open
2. The scraper will attempt to navigate automatically using saved cookies
3. If a CAPTCHA or Cloudflare challenge appears, you'll be prompted to solve it
4. After solving the challenge, type 'done' to continue or 'save' to save cookies
5. The scraper will extract job listings and handle pagination automatically

## 📊 Output

The scraped data is saved in the `output` directory:

- `output/indeed_jobs_[job_title]_[location]_[timestamp].csv`
- `output/indeed_jobs_[job_title]_[location]_[timestamp].json`

Example output structure:
```json
[
  {
    "title": "Senior Software Engineer",
    "company": "Example Tech GmbH",
    "location": "Berlin, Germany",
    "salary": "€65,000 - €85,000 a year",
    "description": "We are looking for a Senior Software Engineer to join our team...",
    "url": "https://de.indeed.com/viewjob?jk=abcd1234",
    "date_posted": "Posted 3 days ago",
    "job_type": "Full-time"
  },
  ...
]
```

## 📁 Project Structure

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

## 🛡️ Handling Anti-Scraping Measures

Indeed.de employs several anti-scraping measures that this project successfully navigates:

1. **Cloudflare Protection**: The scraper uses a combination of cookie management and interactive solving when needed.
2. **Cookie Consent Dialogs**: Automatically detected and handled with fallback to manual intervention.
3. **Rate Limiting**: Implements strategic delays between requests to avoid triggering rate limits.
4. **Browser Fingerprinting**: Uses techniques to make the automated browser appear more like a regular user.

## 🔍 Advanced Usage

### Custom Browser Configuration

The scraper can be configured with different browser options:

```python
from src.manual_scraper import ManualIndeedScraper

# Create a scraper with custom timeout
scraper = ManualIndeedScraper(timeout=120)

# Use the scraper as a context manager
with scraper:
    # Navigate to Indeed.de
    scraper.manual_navigate("https://de.indeed.com/jobs?q=python&l=Berlin")
    
    # Extract job listings
    jobs = scraper.extract_job_listings()
    
    # Print the results
    for job in jobs:
        print(f"{job['title']} at {job['company']} in {job['location']}")
```

## ⚠️ Disclaimer

This project is for educational purposes only. Web scraping may be against the terms of service of some websites.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
