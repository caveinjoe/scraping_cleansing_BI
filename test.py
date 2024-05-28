import pandas as pd

file_path = 'ii16.xls'

tables = pd.read_html(file_path)

df = tables[0]

df.to_excel("test_16.xlsx")