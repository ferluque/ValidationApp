import sqlite3 as sql
import pandas as pd

connection = sql.connect("validation.db")
cur = connection.cursor()

file = pd.read_csv('human_validation.csv').values.tolist()
for i in range(len(file)):
    file[i] = file[i][2:5]

cur.executemany("insert into images values(?, ?, ?)", file)
connection.commit()
connection.close()