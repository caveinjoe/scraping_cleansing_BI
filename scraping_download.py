# Import libraries
from selenium import webdriver 
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import subprocess
from datetime import datetime
from selenium.webdriver.support.ui import Select

# define the url
url= "https://www.bi.go.id/id/statistik/ekonomi-keuangan/sekda/StatistikRegionalDetail.aspx?idprov=14"

# Configure selenium via local driver
options = webdriver.ChromeOptions()
#options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

# print status
print("Please wait, start scraping...")

# solution for timeout
driver.set_page_load_timeout(20)
try:
    driver.get(url)
except TimeoutException:
    driver.execute_script("window.stop();")

# wait for elements to show up
time.sleep(10)

# Drop down menu for selecting province
dropdown_provinsi = driver.find_element(By.ID, "DropDownListProvinsiSekda")
select_provinsi = Select(dropdown_provinsi)
select_provinsi.select_by_visible_text("Bengkulu")

# Refresh the page
driver.refresh()
time.sleep(10)

# Drop down menu for selecting category
dropdown_category = driver.find_element(By.ID, "DropDownListCategorySekda")
select_category = Select(dropdown_provinsi)
select_category.select_by_visible_text("Kegiatan Perbankan")

# Refresh the page
driver.refresh()
time.sleep(10)

driver.quit()