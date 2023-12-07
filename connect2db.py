import pyodbc

# 데이터베이스 연결 설정
server = "127.0.0.1"
username = "sa"
password = "Hotelchat44"
database = "default"
# timeout = 30

cnxn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
    + server
    + ";DATABASE="
    # + database
    + ";UID="
    + username
    + ";PWD="
    + password
    # + ";TIMEOUT="
    # + str(timeout)
)