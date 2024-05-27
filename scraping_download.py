# Import libraries
import time
import os
import httpx
import json
import pandas as pd
from bs4 import BeautifulSoup
from io import BytesIO
from zipfile import ZipFile
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

# import logging
# import http.client

# http.client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

# define the url
base_url= "https://www.bi.go.id/id/statistik/ekonomi-keuangan/sekda/StatistikRegionalDetail.aspx"

# define cache link file
link_file_path = './temp_links.json'

# define category numbers to be scraped
scrape_category_numbers = [4, 16]

# Progress bar
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def validate_datetime(file_path):
    """
    Returns True only if the file specified by 'filename' has been created within a specified time limit.
    
    Parameters:
        filename (str): The path to the file to check for creation time.
        
    Returns:
        bool: True if the file has been created within the specified time limit, False otherwise.
    """
    if os.path.exists(file_path):
        file_creation_time = os.path.getctime(file_path)
        current_time = time.time()
        # Check if the difference is greater than 24 hours (86400 seconds)
        if current_time - file_creation_time < 86400:
            return True
    return False

def validate_link_file(file_path):
    """
    Returns True if the link cache file specified by 'filename' is valid for extraction.
    
    Parameters:
        filename (str): The path to the link cache file to be validated.
        
    Returns:
        bool: True if the link cache file is valid for extraction, False otherwise.
    """
    print("Validating cached links...")

    # Check if the file exists
    file_exists = os.path.exists(file_path)

    # If the file exists and is not stale, load the contents
    if file_exists and validate_datetime(file_path):
        with open(file_path, 'r') as file:
            try:
                content = json.load(file)
            except json.JSONDecodeError:
                return False
    else:
        print("No compatible cache found...")
        return False

    # Check the links
    if isinstance(content, dict):
        for value in content.values():
            if isinstance(value, list):
                for item in value:
                    if all([f'www.bi.go.id' in item, any([f'ii{num:02d}' in item for num in scrape_category_numbers])]):
                        print("Extracting based on cached links...")
                        print(json.dumps(content, indent=4))
                        return True
    print("Getting new links...")
    return False

def get_links(url):
    """
    Returns a dictionary containing the links to be used for extraction.
    
    Parameters:
        url (str): The url of the web page to be scraped.
        
    Returns:
        dict: A dictionary where each key represents a province and its corresponding value is a list of links.
    """
    # print status
    print("Please wait, URL scraping in progress...")

    # Configure selenium via local driver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    # solution for timeout
    driver.set_page_load_timeout(20)
    try:
        driver.get(url)
    except TimeoutException:
        driver.execute_script("window.stop();")

    # Output dict
    category_links = dict()

    # Replaced sleep with wait to improve code efficiency
    try:
        # Drop down menu for selecting province
        # Wait until the dropdown element is present and clickable
        def get_select(id):
            dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, id))
            )
            select = Select(dropdown)
            return select

        select_provinsi = get_select('DropDownListProvinsiSekda')
        total_options = len(select_provinsi.options)
        printProgressBar(0, total_options, prefix = 'Progress:', suffix = 'Complete', length = 50)
        for i in range(total_options):
            # Re-initializing select to avoid staling
            select_provinsi = get_select('DropDownListProvinsiSekda')
            option = select_provinsi.options[i]
            option_value = option.get_attribute('value')
            province_name = option.get_attribute("text")

            # Select the option
            select_provinsi.select_by_value(option_value)

            # Drop down menu for selecting category
            select_category = get_select('DropDownListCategorySekda')

            # Select the option
            select_category.select_by_visible_text("Kegiatan Perbankan")

            # Get XLS file links
            def get_cell_href(number):
                cell_xpath = f'//*[@id="ctl00_ctl54_g_077c3f62_96a4_43aa_b013_8e274cf2ce9d_ctl00_divIsi"]/table/tbody/tr[{number}]/td[2]/a'
                cell_element = driver.find_element(By.XPATH, cell_xpath)
                return cell_element.get_attribute('href')

            link_dict = {province_name: [get_cell_href(number) for number in scrape_category_numbers]}
            category_links.update(link_dict)

            print(f"{link_dict}")   
            printProgressBar(i+1, total_options, prefix = 'Progress:', suffix = 'Complete', length = 50)
        
    finally:
        print(f"CATEGORY: {category_links}")
        driver.quit()
        with open(link_file_path, 'w') as link_file:
            json.dump(category_links, link_file, indent=4)
    
    return category_links

def main():
    if not validate_link_file(link_file_path):
        category_links = get_links(base_url)
    else:
        try:
            with open(link_file_path, 'r') as file:
                category_links = json.load(file)
        except json.JSONDecodeError:
            get_links(base_url)


if __name__ == "__main__":
    main()