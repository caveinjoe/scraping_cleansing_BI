import pandas as pd

# Path ke file yang diunggah
file_path = 'ii04.xls'

# Membaca file Excel
df = pd.read_excel(file_path)

# Menampilkan kolom yang ada untuk referensi
df.show()