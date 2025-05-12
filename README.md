# Myntra Web Scraper

This project scrapes product information from Myntra using Selenium and BeautifulSoup.

## Features

- Scrapes product details including:
  - Brand name
  - Price
  - Original price
  - Product description
  - Sizes
  - Product URL
- Saves data to CSV files in an organized `csv_data` folder
- Maintains logs in a dedicated `logs` folder (logs are overwritten on each run)
- Web UI for easy searching and visualization of results
- Always runs a fresh scrape for each search (forced rescrape)

## Quick Setup Guide

### Prerequisites
- Python 3.8+ installed
- Google Chrome browser installed
- Git (optional, for cloning)

### Installation

**Step 1: Get the Code**  
Either download the ZIP from GitHub or clone the repository:
```
git clone https://github.com/rohan9405/myntra-web-scraper.git
cd myntra-web-scraper
```

**Step 2: Create Virtual Environment**
```
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install Dependencies**
```
pip install -r requirements.txt
```

**Step 4: Run the Application**
```
python simplified_ui.py
```

**Step 5: Access the Web Interface**  
Open your browser and go to:
```
http://127.0.0.1:5000
```

## Using the Web Scraper

1. Enter a search term in the search box (e.g., "jeans", "shirts for men", "dresses")
2. Click "Search Products"
3. Wait for the scraping to complete (this may take 1-2 minutes)
4. View the results, including:
   - Product listings
   - Top brands
   - Price statistics
5. Download the CSV file with the "Download CSV" button

## Troubleshooting

If you encounter issues:

1. **Chrome version mismatch**: The WebDriver Manager should automatically download the correct driver, but if you have issues, ensure your Chrome is up-to-date.

2. **Connection errors**: If Myntra blocks the scraper, try:
   - Reducing the number of pages scraped (modify `no_of_pages` in `modified_myntra_scraper.py`)
   - Adding delays between requests

3. **Installation issues**: Make sure you're using the correct Python version and all dependencies are installed properly.

## Project Structure

```
myntra-scraper/
├── csv_data/           # Contains all scraped CSV files
├── logs/               # Contains all log files
├── templates/          # HTML templates for the web UI
│   ├── index.html      # Landing page with search form
│   └── results.html    # Results page showing scraped data
├── modified_myntra_scraper.py  # Core scraper logic
├── simplified_ui.py    # Flask web interface
├── requirements.txt    # Dependencies
└── README.md           # Project documentation
```

## Notes

- The scraper may be blocked if too many requests are made in a short period.
- Myntra's website structure may change, requiring updates to the scraper.
- Each search term generates a unique file with an incremental number suffix. 