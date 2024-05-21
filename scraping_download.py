# Import libraries
import time
import os
import subprocess
import pandas as pd
from datetime import datetime
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select


# define the url
url= "https://www.bi.go.id/id/statistik/ekonomi-keuangan/sekda/StatistikRegionalDetail.aspx"

# define category numbers to be scraped
scrape_category_numbers = [4, 16]

# Configure selenium via local driver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

# print status
print("Please wait, scraping in progress...")

# solution for timeout
driver.set_page_load_timeout(20)
try:
    driver.get(url)
except TimeoutException:
    driver.execute_script("window.stop();")

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

        # Get XLS file
        def get_cell_href(number):
            cell_xpath = f'//*[@id="ctl00_ctl54_g_077c3f62_96a4_43aa_b013_8e274cf2ce9d_ctl00_divIsi"]/table/tbody/tr[{number}]/td[2]/a'
            cell_element = driver.find_element(By.XPATH, cell_xpath)
            return cell_element.get_attribute('href')

        category_details = [get_cell_href(number) for number in scrape_category_numbers]

        print(f"{province_name} URLS: {category_details}")   
        printProgressBar(i, total_options, prefix = 'Progress:', suffix = 'Complete', length = 50)

finally:
    driver.quit()

