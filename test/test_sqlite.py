import sqlite3

from projects.common import constants

# 建立連線
conn = sqlite3.connect(constants.DB_PATH)

# CREATE TABLE
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("CREATE TABLE IF NOT EXISTS users("
               "id INTEGER PRIMARY KEY, "
               "name TEXT, "
               "email TEXT, "
               "password TEXT)")

conn.commit()
conn.close()

# 執行指令
conn = sqlite3.connect(constants.DB_PATH)
cursor = conn.cursor()
insert_query = "INSERT INTO users VALUES(?, ?, ?, ?)"

users = [(None, "kirai", "abc.def@gmail.com", "123456"),
         (None, "kirai1", "abc1.def@gmail.com", "123456"),
         (None, "kirai2", "abc2.def@gmail.com", "123456")]

cursor.executemany(insert_query, users)

conn.commit()
conn.close()

conn = sqlite3.connect(constants.DB_PATH)
cursor = conn.cursor()
for row in cursor.execute("SELECT * FROM users"):
    print(row)
conn.commit()
conn.close()
