
# Import libraries
import pandas as pd
import re
from enum import Enum

# Globals:
# Propinsi: str

class ProductType(Enum):
    ModalKerja = "Modal Kerja"
    Investasi = "Investasi"
    Konsumsi = "Konsumsi"

class ProductAttr(Enum):
    Nominal = "Nominal"

class Currency(Enum):
    Rupiah = "Rupiah"
    Asing = "Valuta Asing"

def get_years_months(df: pd.DataFrame, year_row: int, month_row: int):
    VALID_MONTHS = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]

    years_months_list = []

    # Extracting the year and month columns
    year_row = df.iloc[year_row]
    year_row_numeric = pd.to_numeric(year_row, errors='coerce')
    year_row_filtered = year_row_numeric.dropna().astype(int).tolist()

    # The first year's column index
    start_x_index = year_row_numeric[year_row_numeric == year_row_filtered[0]].index[0]

    month_row = df.iloc[month_row]
    month_row_filtered = [x for x in month_row.apply(lambda x: x if x in VALID_MONTHS else '' if x in list(map(str, year_row_filtered)) else None).to_list() if x is not None]

    for i in range(len(year_row_filtered)):
        years_months_list.append([year_row_filtered[i], month_row_filtered[i]])

    return years_months_list, start_x_index

def format_data(year: int, month: str, dati_ii: str, details: dict, kurs: Currency):
    formatted_data = [
        {
            "Tahun": year,
            "Bulan": month if month != year else None,
            "Dati II": dati_ii,
            "Kurs": kurs.value,
            ProductType.ModalKerja.value: [
                {
                    ProductAttr.Nominal.value: details[ProductType.ModalKerja]
                }
            ],
            ProductType.Investasi.value: [
                {
                    ProductAttr.Nominal.value: details[ProductType.Investasi]
                }
            ],
            ProductType.Konsumsi.value: [
                {
                    ProductAttr.Nominal.value: details[ProductType.Konsumsi]
                }
            ],
        }
    ]
    return formatted_data

def get_values(df: pd.DataFrame, ym_list, start_x_index):
    
    # Change these based on the row and column index increments per value
    ROW_INDEX_INC = 4
    COL_INDEX_INC = 1
    
    data = []

    def get_province(dfp):
        # Define a regular expression pattern to extract the province name
        pattern = r'PROPINSI\s*([\w\s]+)'

        # Search for the pattern in the first column
        for index, value in dfp[1].items():
            match = re.search(pattern, str(value))
            if match:
                # Extract the province name from the matched pattern
                province = match.group(1).strip()
                break
            else:
                continue
        return province

    # Sheet - wide value
    globals()["Propinsi"] = get_province(df)

    # Row 1 = Nominal, Row 2 = Jumlah
    def get_row_index(dfp, product: ProductType, current_row_index):
        row = dfp.iloc[current_row_index:current_row_index+4, 3] == product.value
        row = row.astype(int).idxmax()
        return row

    # Get the index of rupiah
    rupiah_index = df.index[df.iloc[:, 0] == Currency.Rupiah.value].min()

    # Get the index of foreign currencies
    foreign_index = df.index[df.iloc[:, 0] == Currency.Asing.value].min()

    # Get the index of aggregate values to be excluded
    jumlah_index = df.index[df.iloc[:, 0] == "Jumlah"].min()

    # Start with the lower index
    low_idx, high_idx = (min(rupiah_index, foreign_index), max(rupiah_index, foreign_index))
    sliced_df = df.iloc[low_idx:, 0]
    current_row_index = sliced_df[sliced_df == "1"].index[0]
    curr = Currency.Rupiah if rupiah_index < foreign_index else Currency.Asing

    # Table height
    height = df.shape[0]

    high_flag = False
    while current_row_index < height:
        if current_row_index > high_idx and high_flag == False:
            sliced_df = df.iloc[high_idx:, 0]
            current_row_index = sliced_df[sliced_df == "1"].index[0]
            curr = Currency.Asing if curr != Currency.Asing else Currency.Rupiah
            high_flag = True
        print(curr)
        print(current_row_index)
        if current_row_index > jumlah_index:
            break

        dati_ii = df.iloc[current_row_index, 1]
        if pd.isna(dati_ii) or dati_ii == globals()["Propinsi"]:
            current_row_index += ROW_INDEX_INC
            continue

        current_col_index = start_x_index
        for pair in ym_list:
            year = pair[0]
            month = pair[1]
            details = {}
            for product in ProductType:
                row = get_row_index(df, product, current_row_index)
                details[product] = df.iloc[row, current_col_index]
            kurs = curr
            

            formatted_data = format_data(year, month, dati_ii, details, kurs)

            data.append(formatted_data)

            current_col_index += COL_INDEX_INC  
        current_row_index += ROW_INDEX_INC

    return data

# Function to flatten the JSON structure for multiple years
def flatten_data(data):
    def get_df(inp, record_path):
        df_sub = pd.json_normalize(inp, record_path=[record_path], meta=['Tahun', 'Bulan', 'Dati II', 'Kurs'])
        df_sub['Tipe'] = record_path
        df_sub['Propinsi'] = globals()["Propinsi"]
        return df_sub

    df_all_list = []
    for entry in data:
        df_all_list.extend(get_df(entry, record_path) for record_path in [member.value for member in ProductType])
    
    df_all = pd.concat(df_all_list, ignore_index=True)
    
    return df_all

def Transform16(file_p, excel_file_p):
    print(f"Transforming: {file_p}")
    # Extract years and months
    tables = pd.read_html(file_p)

    # Only has one table
    df = tables[0]

    # Get the years and months as a list
    year_row = 5
    month_row = 6
    ym_list, start_x_index = get_years_months(df, year_row, month_row)

    # Get the formatted data
    data = get_values(df, ym_list, start_x_index)

    # Flatten the data
    df_all = flatten_data(data)

    # Reorder columns
    df_all = df_all[['Propinsi', 'Dati II', 'Tahun', 'Bulan', 'Kurs', 'Tipe', 'Nominal']]

    # Print the DataFrame
    # print(df_all)

    # Save to excel
    df_all.to_excel(excel_file_p, index=False, sheet_name='Summary')
    print(f"Transform Complete. Saved to: {excel_file_p}")

if __name__ == "__main__":
    file_path = "./ii16.xls"
    excel_file_path = "summary_16.xlsx"
    Transform16(file_path, excel_file_path)