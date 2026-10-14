
import pyodbc

server = r"TARUN\SQLEXPRESS"
database = "CustomerSalesIntelligence"
driver = "ODBC Driver 18 for SQL Server"

connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

try:
    with pyodbc.connect(connection_string, timeout=10) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT DB_NAME(), @@SERVERNAME;")
        database_name, server_name = cursor.fetchone()

        print("SQL SERVER CONNECTION SUCCESSFUL")
        print("Database:", database_name)
        print("Server:", server_name)

except pyodbc.Error as error:
    print("SQL SERVER CONNECTION FAILED")
    print(error)
