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
└── README.md           # Project documentation
```

## Requirements

- Python 3.8+
- Chrome browser

## Setup

1. Create a virtual environment:
   ```
   python -m venv selenium_scraper_env
   ```

2. Activate the virtual environment:
   - Windows: 
     ```
     .\selenium_scraper_env\Scripts\activate
     ```
   - macOS/Linux: 
     ```
     source selenium_scraper_env/bin/activate
     ```

3. Install dependencies:
   ```
   pip install pandas beautifulsoup4 requests selenium webdriver-manager flask
   ```

## Running the Web UI

1. With the virtual environment activated, run:
   ```
   python simplified_ui.py
   ```

2. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```

3. Enter a search term (e.g., "jeans", "shoes for women") and click "Search"

4. View the results and download the CSV file if desired

## Running the Scraper Directly

If you prefer to run the scraper without the web UI:

```
python modified_myntra_scraper.py
```

When prompted, enter your search term.

## File Organization

- **CSV Files**: All scraped data is stored in the `csv_data/` directory with filenames based on the search term.
- **Log Files**: All logs are stored in the `logs/` directory, including:
  - Scraper logs
  - Page source files (for debugging)
  - Application logs

## Notes

- The scraper may be blocked if too many requests are made in a short period.
- Myntra's website structure may change, requiring updates to the scraper.
- Each search term generates a unique file, and duplicate searches add a number suffix (e.g., "jeans_1.csv").

## Troubleshooting

If you encounter issues:

1. Make sure Chrome is installed and updated
2. Check that your internet connection is stable
3. Verify that all dependencies are installed correctly
4. If you see "No such element" errors, Myntra may have changed their page structure 