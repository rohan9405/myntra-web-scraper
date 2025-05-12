import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import traceback
import os

# Ensure required directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('csv_data', exist_ok=True)

# Configure logging - use fixed filenames and overwrite
log_path = os.path.join('logs', 'scraper.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='w'),  # Use 'w' mode to overwrite
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to: {log_path}")

def search_url(search_term, page_number):
    template = 'https://www.myntra.com/{}?p={}'
    url = template.format(search_term, page_number)
    logger.debug(f"Generated URL: {url}")
    return url

def scrape_myntra():
    logger.info("Starting Myntra scraper")
    # Setup Chrome with WebDriver Manager
    logger.info("Setting up Chrome WebDriver")
    options = webdriver.ChromeOptions()
    # Uncomment the next line if you want to run Chrome in headless mode
    # options.add_argument('--headless')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        search_term = input('Enter your search term: ')
        logger.info(f"User entered search term: '{search_term}'")
        
        brands = []
        prices = []
        orig_prices = []
        desc = []
        sizes = []
        links = []
        
        no_of_pages = 10  # Scrape 10 pages (about 500 products)
        logger.info(f"Will scrape {no_of_pages} pages")
        
        for page_no in range(1, no_of_pages + 1):
            logger.info(f"Scraping page {page_no} of {no_of_pages}")
            url = search_url(search_term, page_no)
            logger.debug(f"Navigating to URL: {url}")
            
            driver.get(url)
            logger.debug("Waiting for page to load")
            time.sleep(3)  # Wait for dynamic content to load
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            logger.debug("Parsing page with BeautifulSoup")
            
            # Find all product items
            products = soup.find_all('li', class_='product-base')
            logger.info(f"Found {len(products)} products on page {page_no}")
            
            for product in products:
                try:
                    # Extract brand
                    brand_elem = product.find('h3', class_='product-brand')
                    brand = brand_elem.text.strip() if brand_elem else "N/A"
                    brands.append(brand)
                    
                    # Extract price
                    price_elem = product.find('span', class_='product-discountedPrice')
                    if not price_elem:
                        price_elem = product.find('div', class_='product-price')
                    price = price_elem.text.strip() if price_elem else "N/A"
                    # Remove 'Rs. ' from the price
                    price = price.replace('Rs. ', '') if price != "N/A" else price
                    prices.append(price)
                    
                    # Extract original price
                    orig_price_elem = product.find('span', class_='product-strike')
                    orig_price = orig_price_elem.text.strip() if orig_price_elem else "N/A"
                    # Remove 'Rs. ' from the original price
                    orig_price = orig_price.replace('Rs. ', '') if orig_price != "N/A" else orig_price
                    orig_prices.append(orig_price)
                    
                    # Extract product description
                    desc_elem = product.find('h4', class_='product-product')
                    description = desc_elem.text.strip() if desc_elem else "N/A"
                    desc.append(description)
                    
                    # Extract sizes
                    sizes_elem = product.find('h4', class_='product-sizes')
                    size = sizes_elem.text.strip() if sizes_elem else "N/A"
                    sizes.append(size)
                    
                    # Extract product link
                    link_elem = product.find('a')
                    link = "https://www.myntra.com" + link_elem['href'] if link_elem and 'href' in link_elem.attrs else "N/A"
                    links.append(link)
                    
                except Exception as e:
                    logger.error(f"Error extracting data from product: {str(e)}")
                    # Append N/A for any missing data
                    if len(brands) < len(prices):
                        brands.append("N/A")
                    if len(prices) < len(brands):
                        prices.append("N/A")
                    if len(orig_prices) < len(brands):
                        orig_prices.append("N/A")
                    if len(desc) < len(brands):
                        desc.append("N/A")
                    if len(sizes) < len(brands):
                        sizes.append("N/A")
                    if len(links) < len(brands):
                        links.append("N/A")
            
            logger.info(f"Completed scraping page {page_no}")
        
        # Close the webdriver
        logger.info("Closing WebDriver")
        driver.quit()
        
        # Create DataFrame
        logger.info("Creating DataFrame with scraped data")
        df = pd.DataFrame({
            'brand_name': brands,
            'price': prices,
            'original_price': orig_prices,
            'description': desc,
            'sizes': sizes,
            'product_url': links
        })
        
        # Save to CSV
        csv_name = f"myntra_products_{search_term.replace(' ', '_')}.csv"
        csv_filename = get_unique_filename('csv_data', csv_name)
        csv_path = os.path.join('csv_data', csv_filename)
        
        logger.info(f"Saving data to CSV: {csv_path}")
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(df)} products to {csv_path}")
        
        return df
        
    except Exception as e:
        logger.critical(f"Critical error in scraper: {str(e)}")
        logger.critical(traceback.format_exc())
        
        # Make sure to close the driver in case of error
        try:
            if driver:
                driver.quit()
        except:
            pass
        
        # Return empty DataFrame in case of error
        return pd.DataFrame()

# Function to generate a unique filename if a file already exists
def get_unique_filename(folder, filename):
    """Generate a unique filename by adding a number suffix if the file already exists"""
    base_name, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{base_name}_{counter}{extension}"
        counter += 1
        
    return new_filename

if __name__ == "__main__":
    logger.info("Running scraper from main")
    try:
        df = scrape_myntra()
        logger.info(f"Scraper completed successfully. Scraped {len(df)} products.")
    except Exception as e:
        logger.critical(f"Fatal error in main: {str(e)}")
        logger.critical(traceback.format_exc()) 