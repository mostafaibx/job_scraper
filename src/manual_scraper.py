#!/usr/bin/env python3
"""
Manual scraper for Indeed.de that helps with Cloudflare protection.
"""
import time
import json
import pickle
import logging
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from utils import build_indeed_url, get_config, save_to_csv, save_to_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ManualIndeedScraper:
    """
    A manual scraper for Indeed.de job listings that helps with Cloudflare protection.
    """
    
    def __init__(self, timeout=60):
        """
        Initialize the scraper.
        
        Args:
            timeout (int): Timeout for page loading in seconds
        """
        self.timeout = timeout
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, timeout)
        self.cookies_file = Path("indeed_cookies.pkl")
        


    # setting up the driver while taking into account 
    ##### the Docker environment 
    ##### the performance 
    ##### detection of the scraper by the website
    def _setup_driver(self):
        """
        Set up the Chrome WebDriver.
        
        Returns:
            WebDriver: Configured Chrome WebDriver
        """
        chrome_options = Options()
        
        # Add additional options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # Set user agent to a more recent one
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
        
        # Add additional options to avoid detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Install and set up Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute CDP commands to avoid detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        return driver
    
    def close(self):
        """
        Close the WebDriver.
        """
        if self.driver:
            self.driver.quit()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def load_cookies(self):
        """
        Load cookies from file if available.
        
        Returns:
            bool: True if cookies were loaded successfully, False otherwise
        """
        if not self.cookies_file.exists():
            logger.info("No cookies file found.")
            return False
        
        try:
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            
            # First, navigate to the domain
            self.driver.get("https://de.indeed.com")
            time.sleep(2)
            
            # Add the cookies
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Error adding cookie: {str(e)}")
            
            logger.info("Cookies loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
            return False
    
    def save_cookies(self):
        """
        Save cookies to file.
        
        Returns:
            bool: True if cookies were saved successfully, False otherwise
        """
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            logger.info(f"Cookies saved to {self.cookies_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving cookies: {str(e)}")
            return False
    
    def manual_navigate(self, url):
        """
        Navigate to the specified URL and let the user handle any challenges.
        
        Args:
            url (str): URL to navigate to
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        logger.info(f"Navigating to {url}")
        
        # Try to load cookies first
        cookies_loaded = self.load_cookies()
        
        # Navigate to the URL
        self.driver.get(url)
        
        # Check if we need to show the manual navigation prompt
        # We'll check if job listings are visible, which indicates successful navigation
        try:
            # Wait a moment for the page to load
            time.sleep(3)
            
            # Try to find job listings using different selectors
            job_cards_found = False
            selectors = [
                "div[data-testid='jobCard']",
                ".jobsearch-ResultsList > div",
                "#mosaic-provider-jobcards .job_seen_beacon"
            ]
            
            for selector in selectors:
                try:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards and len(job_cards) > 0:
                        logger.info(f"Found {len(job_cards)} job cards using selector: {selector}")
                        job_cards_found = True
                        break
                except:
                    continue
            
            # Check for Cloudflare challenge or CAPTCHA
            cloudflare_elements = [
                (By.ID, "challenge-running"),
                (By.ID, "cf-challenge-running"),
                (By.CLASS_NAME, "cf-browser-verification"),
                (By.CLASS_NAME, "cf-im-under-attack"),
                (By.CSS_SELECTOR, "div.cf-wrapper"),
                (By.XPATH, "//*[contains(text(), 'Checking your browser')]"),
                (By.XPATH, "//*[contains(text(), 'Please wait')]"),
                (By.XPATH, "//*[contains(text(), 'DDoS protection')]"),
                (By.ID, "captcha"),
                (By.CLASS_NAME, "g-recaptcha"),
                (By.XPATH, "//*[contains(text(), 'CAPTCHA')]"),
                (By.XPATH, "//*[contains(text(), 'captcha')]"),
                (By.XPATH, "//*[contains(text(), 'I am human')]")
            ]
            
            challenge_found = False
            for element_type, element_value in cloudflare_elements:
                if self.driver.find_elements(element_type, element_value):
                    challenge_found = True
                    break
            
            # Check for cookie consent dialog
            cookie_dialog_found = False
            try:
                overlays = self.driver.find_elements(By.CSS_SELECTOR, ".overlay, .modal, .dialog, .popup, .consent, .cookie")
                if overlays:
                    cookie_dialog_found = True
            except:
                pass
            
            # If we found job cards and no challenges, we can proceed without manual intervention
            if job_cards_found and not challenge_found and not cookie_dialog_found:
                logger.info("Successfully navigated to job listings without manual intervention.")
                return True
            
            # Otherwise, we need manual intervention
            print("\n" + "="*80)
            print("MANUAL NAVIGATION MODE")
            print("1. If you see a CAPTCHA or Cloudflare challenge, please solve it.")
            print("2. Navigate to the job search results page if needed.")
            print("3. Once you can see the job listings, type 'done' and press Enter.")
            print("4. To save cookies for future use, type 'save' and press Enter.")
            print("5. To quit without saving, type 'quit' and press Enter.")
            print("="*80 + "\n")
            
            while True:
                user_input = input("Command (done/save/quit): ").strip().lower()
                
                if user_input == 'done':
                    logger.info("Continuing with scraping...")
                    break
                elif user_input == 'save':
                    self.save_cookies()
                    logger.info("Continuing with scraping...")
                    break
                elif user_input == 'quit':
                    logger.info("Quitting...")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error during navigation: {str(e)}")
            
            # If there's an error, fall back to manual navigation
            print("\n" + "="*80)
            print("MANUAL NAVIGATION MODE")
            print("1. If you see a CAPTCHA or Cloudflare challenge, please solve it.")
            print("2. Navigate to the job search results page if needed.")
            print("3. Once you can see the job listings, type 'done' and press Enter.")
            print("4. To save cookies for future use, type 'save' and press Enter.")
            print("5. To quit without saving, type 'quit' and press Enter.")
            print("="*80 + "\n")
            
            while True:
                user_input = input("Command (done/save/quit): ").strip().lower()
                
                if user_input == 'done':
                    logger.info("Continuing with scraping...")
                    break
                elif user_input == 'save':
                    self.save_cookies()
                    logger.info("Continuing with scraping...")
                    break
                elif user_input == 'quit':
                    logger.info("Quitting...")
                    return False
            
            return True
    
    def extract_job_listings(self):
        """
        Extract job listings from the current page.
        
        Returns:
            list: List of job dictionaries
        """
        jobs = []
        
        try:
            # Try different selectors for job cards
            job_cards = None
            selectors = [
                "div[data-testid='jobCard']",
                ".jobsearch-ResultsList > div",
                "#mosaic-provider-jobcards .job_seen_beacon"
            ]
            
            for selector in selectors:
                try:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards and len(job_cards) > 0:
                        logger.info(f"Found {len(job_cards)} job cards using selector: {selector}")
                        break
                except:
                    continue
            
            if not job_cards or len(job_cards) == 0:
                logger.warning("No job cards found.")
                return []
            
            for card in job_cards:
                try:
                    job_data = self._extract_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.warning(f"Error extracting job data: {str(e)}")
                    continue
                    
            return jobs
        except Exception as e:
            logger.error(f"Error extracting job listings: {str(e)}")
            return []
    
    def _extract_job_data(self, card):
        """
        Extract data from a job card.
        
        Args:
            card (WebElement): Job card element
            
        Returns:
            dict: Job data dictionary
        """
        job = {}
        
        try:
            # Try different selectors for job title
            title_selectors = [
                "h2.jobTitle span",
                "h2.jobTitle a span",
                "a.jcs-JobTitle span",
                ".jobTitle"
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job['title'] = title_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            if 'title' not in job:
                job['title'] = "Title not found"
            
            # Extract company name
            company_selectors = [
                "span[data-testid='company-name']",
                ".companyName",
                ".company_location .companyName"
            ]
            
            for selector in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job['company'] = company_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            if 'company' not in job:
                job['company'] = "Company not found"
            
            # Extract location
            location_selectors = [
                "div[data-testid='text-location']",
                ".companyLocation",
                ".company_location .companyLocation"
            ]
            
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job['location'] = location_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            if 'location' not in job:
                job['location'] = "Location not found"
            
            # Extract salary if available
            salary_selectors = [
                "div[data-testid='attribute_snippet_testid']",
                ".salary-snippet",
                ".salaryOnly"
            ]
            
            for selector in salary_selectors:
                try:
                    salary_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job['salary'] = salary_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            if 'salary' not in job:
                job['salary'] = "Not specified"
            
            # Extract job URL
            url_selectors = [
                "h2.jobTitle a",
                "a.jcs-JobTitle",
                ".jobTitle a"
            ]
            
            for selector in url_selectors:
                try:
                    link_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job['url'] = link_elem.get_attribute("href")
                    job['job_id'] = job['url'].split('jk=')[1].split('&')[0] if 'jk=' in job['url'] else "unknown"
                    break
                except (NoSuchElementException, IndexError):
                    continue
            
            if 'url' not in job:
                job['url'] = "Not available"
                job['job_id'] = "unknown"
            
            # Extract job snippet/description
            snippet_selectors = [
                "div.job-snippet",
                ".job-snippet",
                ".job-snippet-container"
            ]
            
            for selector in snippet_selectors:
                try:
                    snippet_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job['snippet'] = snippet_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            if 'snippet' not in job:
                job['snippet'] = "Not available"
            
            # Extract date posted
            date_selectors = [
                "span.date",
                ".date",
                ".new"
            ]
            
            for selector in date_selectors:
                try:
                    date_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job['date_posted'] = date_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            if 'date_posted' not in job:
                job['date_posted'] = "Not specified"
            
            return job
        except Exception as e:
            logger.warning(f"Error extracting job data from card: {str(e)}")
            return None
    
    def has_next_page(self):
        """
        Check if there is a next page of results.
        
        Returns:
            bool: True if there is a next page, False otherwise
        """
        try:
            # Try different selectors for next page button
            next_selectors = [
                "a[data-testid='pagination-page-next']",
                "a.pn",
                "a[aria-label='Next']",
                "a.np"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return True
                except NoSuchElementException:
                    continue
            
            return False
        except Exception as e:
            logger.error(f"Error checking for next page: {str(e)}")
            return False
    
    def go_to_next_page(self):
        """
        Navigate to the next page of results.
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            # First, check for and handle any cookie consent dialogs that might be in the way
            cookie_handled = self._handle_cookie_consent()
            
            # Try different selectors for next page button
            next_selectors = [
                "a[data-testid='pagination-page-next']",
                "a.pn",
                "a[aria-label='Next']",
                "a.np"
            ]
            
            next_button = None
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not next_button:
                logger.warning("No next page button found")
                return False
            
            # Try to scroll to the button to make it visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            
            # Try to click the button
            try:
                next_button.click()
            except Exception as e:
                logger.warning(f"Could not click next button directly: {str(e)}")
                # Try JavaScript click as a fallback
                self.driver.execute_script("arguments[0].click();", next_button)
            
            time.sleep(3)  # Wait for the page to load
            
            # Check if we successfully navigated to the next page
            # Try to find job listings using different selectors
            job_cards_found = False
            selectors = [
                "div[data-testid='jobCard']",
                ".jobsearch-ResultsList > div",
                "#mosaic-provider-jobcards .job_seen_beacon"
            ]
            
            for selector in selectors:
                try:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards and len(job_cards) > 0:
                        logger.info(f"Found {len(job_cards)} job cards on next page using selector: {selector}")
                        job_cards_found = True
                        break
                except:
                    continue
            
            # If we found job cards, we successfully navigated to the next page
            if job_cards_found:
                return True
                
            # If we didn't find job cards or there was a cookie consent dialog that wasn't handled automatically,
            # we need manual intervention
            if not job_cards_found or not cookie_handled:
                # If we failed, ask the user to navigate manually
                print("\n" + "="*80)
                print("MANUAL NAVIGATION NEEDED")
                print("Please navigate to the next page manually.")
                print("Once you're on the next page, type 'done' and press Enter.")
                print("To quit, type 'quit' and press Enter.")
                print("="*80 + "\n")
                
                user_input = input("Command (done/quit): ").strip().lower()
                if user_input == 'done':
                    logger.info("Continuing with scraping...")
                    return True
                else:
                    logger.info("Manual navigation aborted.")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error navigating to next page: {str(e)}")
            
            # If we failed, ask the user to navigate manually
            print("\n" + "="*80)
            print("MANUAL NAVIGATION NEEDED")
            print("Please navigate to the next page manually.")
            print("Once you're on the next page, type 'done' and press Enter.")
            print("To quit, type 'quit' and press Enter.")
            print("="*80 + "\n")
            
            user_input = input("Command (done/quit): ").strip().lower()
            if user_input == 'done':
                logger.info("Continuing with scraping...")
                return True
            else:
                logger.info("Manual navigation aborted.")
                return False
    
    def _handle_cookie_consent(self):
        """
        Handle cookie consent dialog if it appears.
        
        Returns:
            bool: True if handled automatically, False if manual intervention is needed
        """
        try:
            # Look for cookie consent button and click it if found
            cookie_buttons = [
                (By.ID, "onetrust-accept-btn-handler"),
                (By.ID, "accept-cookie-notification"),
                (By.CSS_SELECTOR, "button[data-testid='cookie-consent-accept']"),
                (By.CSS_SELECTOR, ".accept-cookies-button"),
                (By.CSS_SELECTOR, "#onetrust-accept-btn-handler"),
                (By.CSS_SELECTOR, "button.onetrust-close-btn-handler"),
                (By.CSS_SELECTOR, "button.cookie-consent-accept"),
                (By.XPATH, "//button[contains(text(), 'Accept')]"),
                (By.XPATH, "//button[contains(text(), 'Accept All')]"),
                (By.XPATH, "//button[contains(text(), 'I Accept')]"),
                (By.XPATH, "//button[contains(text(), 'Agree')]"),
                (By.XPATH, "//button[contains(text(), 'OK')]"),
                (By.XPATH, "//button[contains(text(), 'Got it')]")
            ]
            
            for button_type, button_value in cookie_buttons:
                try:
                    cookie_buttons = self.driver.find_elements(button_type, button_value)
                    if cookie_buttons:
                        for button in cookie_buttons:
                            try:
                                # Try to scroll to the button to make it visible
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(0.5)
                                
                                # Try to click the button
                                try:
                                    button.click()
                                except:
                                    # Try JavaScript click as a fallback
                                    self.driver.execute_script("arguments[0].click();", button)
                                
                                logger.info(f"Accepted cookies using {button_type}={button_value}")
                                time.sleep(1)  # Wait for dialog to disappear
                                return True
                            except:
                                continue
                except:
                    continue
                
        except Exception as e:
            logger.warning(f"Error handling cookie consent: {str(e)}")
            
        # If we couldn't handle it automatically, check if there's a visible overlay
        try:
            # Check if there's any visible overlay or dialog
            overlays = self.driver.find_elements(By.CSS_SELECTOR, ".overlay, .modal, .dialog, .popup, .consent, .cookie")
            if overlays:
                # Only return False if we actually found overlays that need manual handling
                return False
        except:
            pass
            
        # If we didn't find any overlays or couldn't detect them, assume everything is fine
        return True
