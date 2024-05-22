
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

file_path = "./32-ii04.zip"

with ZipFile(file_path) as zipfile:
    # Extract each file in the ZIP archive
    for file_name in zipfile.namelist():
        with zipfile.open(file_name) as extracted_file:
            print(f"Extracting: {file_name}")
            soup = BeautifulSoup(extracted_file, 'html.parser')
            # Extracting the years from the relevant <td> tags  
            year_row = soup.find('tr', class_='xl25')
            years = []
            if year_row:
                cells = year_row.find_all('td')
                print(cells)
                for cell in cells:
                    if 'x:num' in cell.attrs:
                        year = cell.get_text(strip=True)
                        years.extend([year])
            print(f"YEARS: {years}")