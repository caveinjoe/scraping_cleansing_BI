
# Import libraries
import time
import os
import httpx
import json
import pandas as pd
import openpyxl
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
excel_file_path = "summary_04.xlsx"

with ZipFile(file_path) as zipfile:
    # Extract each file in the ZIP archive
    for file_name in zipfile.namelist():
        with zipfile.open(file_name) as extracted_file:
            print(f"Extracting: {file_name}")
            soup = BeautifulSoup(extracted_file, 'html.parser')
            # Extract years and months
            data = []

            # First row with years
            year_row = soup.find('tr', class_='xl25')
            year_cells = year_row.find_all('td')
            years_with_months = {}
            years = []

            # Second row with months
            month_row = soup.find('tr', class_='xl29')
            month_cells = month_row.find_all('td')

            # Extract years and months
            for cell in year_cells:
                if 'x:num' in cell.attrs:
                    year = cell.get_text(strip=True)
                    if cell.has_attr('rowspan'):
                        years.append(year)
                    elif cell.has_attr('colspan'):
                        if year not in years_with_months:
                            years_with_months[year] = {
                                "num_months": int(cell['colspan']),
                                "months": list()
                            }
                        else:
                            years_with_months[year]["num_months"] += int(cell['colspan'])
            
            # Extract months only if there are months cells
            if years_with_months:
                months = [cell.get_text() for cell in month_cells]

                print(years_with_months)
                print(months)

                # Adding months to years with months
                for year_m in years_with_months.keys():
                    print([months[i] for i in range(years_with_months[year_m]["num_months"])])
                    years_with_months[year_m]["months"] = [months[i] for i in range(years_with_months[year_m]["num_months"])]

            # Fill the data list with years and months
            for year in years:
                data.append([year, ""])
            for year in years_with_months.keys():
                for i in range(years_with_months[year]["num_months"]):
                    data.append([year, years_with_months[year]["months"][i]])
            print(data)
            # Define the order of months
            months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

            # Function to sort the list
            def sort_data(dt):
            # Sort by year first, then by month
                return sorted(dt, key=lambda x: (x[0], months_order.index(x[1])))

            # Convert to DataFrame
            df = pd.DataFrame(data, columns=["Tahun", "Bulan"])
            print(df)

            # Specify mode='w' to overwrite the existing file
            df.to_excel(excel_file_path, index=False, sheet_name='Summary')

            # # Load the workbook and the active sheet
            # with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            #     workbook = writer.book
            #     worksheet = workbook['Summary']

            #     # Apply borders to all cells in the worksheet
            #     for row in worksheet.iter_rows():
            #         for cell in row:
            #             cell.border = openpyxl.styles.Border(
            #                 left=openpyxl.styles.Side(border_style='thin', color='000000'),
            #                 right=openpyxl.styles.Side(border_style='thin', color='000000'),
            #                 top=openpyxl.styles.Side(border_style='thin', color='000000'),
            #                 bottom=openpyxl.styles.Side(border_style='thin', color='000000')
            #             )

            #     # Save the workbook
            #     writer.save()