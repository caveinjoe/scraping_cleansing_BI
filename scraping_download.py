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

# define the url
url= "https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/Default.aspx"

# Configure selenium via local driver
options = webdriver.ChromeOptions()
#options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

# print status
print("Please wait, start scraping...")


