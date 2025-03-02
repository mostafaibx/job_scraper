"""
Tests for utility functions.
"""
import unittest
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils import build_indeed_url

class TestUtils(unittest.TestCase):
    """
    Test utility functions.
    """
    
    def test_build_indeed_url(self):
        """
        Test building Indeed.de URLs.
        """
        # Test basic URL
        url = build_indeed_url("software engineer", "Berlin", 25)
        self.assertEqual(
            url,
            "https://de.indeed.com/jobs?q=software+engineer&l=Berlin&radius=25&limit=15"
        )
        
        # Test URL with pagination
        url = build_indeed_url("data scientist", "Munich", 10, start=30, limit=20)
        self.assertEqual(
            url,
            "https://de.indeed.com/jobs?q=data+scientist&l=Munich&radius=10&limit=20&start=30"
        )
        
        # Test URL with special characters
        url = build_indeed_url("C++ developer", "Frankfurt am Main", 15)
        self.assertEqual(
            url,
            "https://de.indeed.com/jobs?q=C+++developer&l=Frankfurt+am+Main&radius=15&limit=15"
        )

if __name__ == "__main__":
    unittest.main() 