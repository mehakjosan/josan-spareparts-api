import pandas as pd
import pyodbc

file_path = r"C:\Users\dell\Downloads\tblCustomer_1000.xlsx"

df = pd.read_excel(file_path)

conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=SprayerPartsDB;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO tblCustomer
        (
            CustomerName,
            Address,
            ContactNo,
            Email,
            GSTNo,
            CustomerType
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    row["CustomerName"],
    row["Address"],
    str(row["ContactNo"]),
    row["Email"],
    row["GSTNo"],
    row["CustomerType"]
    )

conn.commit()

print("1000 Customers Imported Successfully!")

cursor.close()
conn.close()