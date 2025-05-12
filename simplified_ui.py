import os
import subprocess
import pandas as pd
import logging
import traceback
import sys
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import time
import re

# Ensure required directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('csv_data', exist_ok=True)

# Function to generate a unique filename if a file already exists - keep this for CSV files
def get_unique_filename(folder, filename):
    """Generate a unique filename by adding a number suffix if the file already exists"""
    base_name, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{base_name}_{counter}{extension}"
        counter += 1
        
    return new_filename

# Configure logging - use fixed names and overwrite files
log_path = os.path.join('logs', 'ui_app.log')

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

app = Flask(__name__)

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    search_term = request.form.get('search_term', '')
    if not search_term:
        logger.warning("No search term provided")
        return render_template('index.html', error="Please enter a search term")

    logger.info(f"Starting scrape for search term: '{search_term}'")
    
    # Create the CSV filename based on the search term
    csv_base_filename = f"myntra_products_{search_term.replace(' ', '_')}.csv"
    csv_filename = get_unique_filename('csv_data', csv_base_filename)
    csv_filepath = os.path.join('csv_data', csv_filename)
    
    logger.info(f"CSV file will be: {csv_filepath}")
    
    # Always perform a new scrape
    logger.info(f"Starting fresh scrape for '{search_term}'")
    
    # Create a direct test script that uses modified_myntra_scraper
    tmp_script_path = 'tmp_script.py'
    logger.info(f"Creating temporary script: {tmp_script_path}")
    
    # Set fixed log paths for subprocess
    tmp_script_log_path = os.path.join('logs', 'tmp_script.log')
    stdout_log_path = os.path.join('logs', f"subprocess_stdout.log")
    stderr_log_path = os.path.join('logs', f"subprocess_stderr.log")
    
    with open(tmp_script_path, 'w') as f:
        f.write(f'''
import sys
import os
import logging
import traceback
import pandas as pd

# Ensure required directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('csv_data', exist_ok=True)

# Configure logging - use fixed filename and overwrite
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("{tmp_script_log_path.replace('\\', '\\\\')}", mode='w'),  # Overwrite mode
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tmp_script")

logger.info("Starting temporary script")
logger.info(f"Python executable: {{sys.executable}}")
logger.info(f"Python version: {{sys.version}}")
logger.info(f"Current directory: {{os.getcwd()}}")

# Function to generate a unique filename if a file already exists
def get_unique_filename(folder, filename):
    """Generate a unique filename by adding a number suffix if the file already exists"""
    base_name, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{{base_name}}_{{counter}}{{extension}}"
        counter += 1
        
    return new_filename

try:
    logger.info("Importing modified_myntra_scraper")
    import modified_myntra_scraper
    
    # Modify the scraper's save path to use csv_data folder
    orig_scrape_myntra = modified_myntra_scraper.scrape_myntra
    
    def wrapped_scrape_myntra():
        # Override the scraper's CSV output path
        orig_to_csv = pd.DataFrame.to_csv
        
        def patched_to_csv(self, *args, **kwargs):
            if args and isinstance(args[0], str):
                # Get the original filename from args
                orig_filename = args[0]
                basename = os.path.basename(orig_filename)
                
                # Create a new path in the csv_data folder
                new_filename = get_unique_filename('csv_data', basename)
                new_path = os.path.join('csv_data', new_filename)
                
                logger.info(f"Redirecting CSV output from {{orig_filename}} to {{new_path}}")
                
                # Replace the first arg (the filename)
                args_list = list(args)
                args_list[0] = new_path
                args = tuple(args_list)
            
            # Call the original to_csv method
            return orig_to_csv(self, *args, **kwargs)
        
        # Apply the patch
        pd.DataFrame.to_csv = patched_to_csv
        
        # Call the original scrape_myntra function
        result = orig_scrape_myntra()
        
        # Restore the original to_csv method
        pd.DataFrame.to_csv = orig_to_csv
        
        return result
    
    # Replace the original function with our wrapped version
    modified_myntra_scraper.scrape_myntra = wrapped_scrape_myntra
    
    # Override input function to return the search term
    def mock_input(prompt):
        logger.info(f"Mock input called with prompt: {{prompt}}")
        return "{search_term}"
    
    # Replace the built-in input function with our mock
    modified_myntra_scraper.input = mock_input
    logger.info(f"Replaced input function to return '{search_term}'")
    
    # Run the scraper
    logger.info("About to call scrape_myntra()")
    df = modified_myntra_scraper.scrape_myntra()
    
    # Check for CSV files in the csv_data directory
    csv_files = [f for f in os.listdir('csv_data') if f.endswith('.csv')]
    search_term_files = [f for f in csv_files if f.startswith(f"myntra_products_{search_term.replace(' ', '_')}")]
    
    if search_term_files:
        # Get the most recent file
        latest_file = max(search_term_files, key=lambda f: os.path.getmtime(os.path.join('csv_data', f)))
        csv_path = os.path.join('csv_data', latest_file)
        
        if os.path.exists(csv_path):
            file_size = os.path.getsize(csv_path)
            row_count = len(df) if df is not None else "unknown"
            logger.info(f"Scraping completed. CSV file exists at {{csv_path}}. Size: {{file_size}} bytes, Rows: {{row_count}}")
        else:
            logger.error(f"Scraping might have failed. CSV file {{csv_path}} does not exist.")
    else:
        logger.error(f"No CSV files found for search term: {search_term}")
    
except Exception as e:
    logger.critical(f"Critical error in tmp_script: {{str(e)}}")
    logger.critical(traceback.format_exc())
    raise
''')
    
    logger.info("Running the temporary script")
    try:
        # Run the script and capture output
        process = subprocess.Popen([sys.executable, tmp_script_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        stdout, stderr = process.communicate(timeout=180)  # 3 minute timeout
        
        stdout_str = stdout.decode('utf-8', errors='replace') if stdout else "None"
        stderr_str = stderr.decode('utf-8', errors='replace') if stderr else "None"
        
        logger.info(f"Subprocess return code: {process.returncode}")
        logger.info(f"Subprocess stdout: {stdout_str[:500]}...")  # Log first 500 chars
        logger.info(f"Subprocess stderr: {stderr_str[:500]}...")  # Log first 500 chars
        
        # Write full output to log files for debugging
        with open(stdout_log_path, "w", encoding="utf-8") as f:
            f.write(stdout_str)
        with open(stderr_log_path, "w", encoding="utf-8") as f:
            f.write(stderr_str)
        
        if process.returncode != 0:
            logger.error(f"Subprocess failed with return code {process.returncode}")
            return render_template('index.html', 
                                error=f"Error scraping data. Check logs for details.")
        
    except subprocess.TimeoutExpired:
        logger.error("Subprocess timed out after 3 minutes")
        process.kill()
        return render_template('index.html', 
                             error="Scraping timed out. The website might be slow or blocking automated access.")
    except Exception as e:
        logger.exception(f"Exception while running scraper: {str(e)}")
        return render_template('index.html', 
                             error=f"Error running scraper: {str(e)}")
    finally:
        # Always try to clean up the temporary script
        try:
            logger.info(f"Removing temporary script: {tmp_script_path}")
            if os.path.exists(tmp_script_path):
                os.remove(tmp_script_path)
        except Exception as e:
            logger.error(f"Error removing temporary script: {str(e)}")
    
    # Check for the log file from the scraper
    scraper_log = os.path.join('logs', 'scraper.log')
    if os.path.exists(scraper_log):
        logger.info(f"Scraper log file exists at {scraper_log}, reading last 50 lines")
        try:
            with open(scraper_log, "r", encoding="utf-8") as f:
                log_lines = f.readlines()
                last_lines = log_lines[-50:] if len(log_lines) > 50 else log_lines
                logger.info(f"Last lines from scraper.log: {''.join(last_lines)}")
        except Exception as e:
            logger.error(f"Error reading scraper log: {str(e)}")
    
    # Find the most recent CSV file for this search term in the csv_data directory
    csv_pattern = re.compile(fr"myntra_products_{re.escape(search_term.replace(' ', '_'))}.*\.csv$")
    matching_files = [f for f in os.listdir('csv_data') if csv_pattern.match(f)]
    
    if not matching_files:
        logger.error(f"No CSV files found for search term '{search_term}' in csv_data directory")
        return render_template('index.html', 
                             error=f"No results found for '{search_term}'. The website might have changed or is blocking scrapers.")
    
    # Get the most recent file
    latest_csv = max(matching_files, key=lambda f: os.path.getmtime(os.path.join('csv_data', f)))
    latest_csv_path = os.path.join('csv_data', latest_csv)
    
    logger.info(f"Found CSV file: {latest_csv_path}")
    return process_results(search_term, latest_csv_path)

def process_results(search_term, csv_filepath):
    """Process the CSV results and render the template"""
    logger.info(f"Processing results from {csv_filepath}")
    
    # Read the CSV data
    try:
        df = pd.read_csv(csv_filepath)
        logger.info(f"CSV loaded successfully. Shape: {df.shape}")
        
        if len(df) == 0:
            logger.warning("CSV file is empty")
            return render_template('index.html', 
                                error=f"No results found for '{search_term}'")
    except Exception as e:
        logger.exception(f"Error reading CSV file: {str(e)}")
        return render_template('index.html', 
                             error=f"Error reading data: {str(e)}")
    
    # Generate analytics
    logger.info("Generating analytics")
    analytics = {
        "total_products": len(df),
        "top_brands": df['brand_name'].value_counts().head(10).to_dict() if 'brand_name' in df.columns else {},
        "price_range": {
            "min": df['price'].min() if 'price' in df.columns and not pd.isna(df['price']).all() else 0,
            "max": df['price'].max() if 'price' in df.columns and not pd.isna(df['price']).all() else 0,
            "avg": round(df['price'].mean(), 2) if 'price' in df.columns and not pd.isna(df['price']).all() else 0
        }
    }
    
    # Prepare data for template (first 20 rows)
    products = df.head(20).to_dict('records')
    logger.info(f"Rendering results template with {len(products)} products")
    
    # Extract just the filename for the download link
    csv_filename = os.path.basename(csv_filepath)
    
    return render_template('results.html', 
                          search_term=search_term,
                          products=products, 
                          total_products=len(df),
                          analytics=analytics,
                          csv_file=csv_filename)

@app.route('/download/<filename>')
def download(filename):
    logger.info(f"Downloading file: {filename}")
    filepath = os.path.join('csv_data', filename)
    
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return "File not found", 404
        
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('csv_data', exist_ok=True)
    
    logger.info("Starting Flask app")
    app.run(debug=True, use_reloader=False, port=5000) 