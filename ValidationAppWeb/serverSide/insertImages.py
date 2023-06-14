import sqlite3 as sql
import pandas as pd

connection = sql.connect("validation.db")
cur = connection.cursor()
cur.execute("pragma foreign_keys=ON")

file = pd.read_csv('human_validation.csv').values.tolist()
print(file)

for _,_,f, a, c in file:
    cur.execute("insert into images (file_name) values (\""+f+"\")")
    cur.execute("insert into modelOutput (file_name, act_name, cat_name) values (\""+f+"\", \""+ a+ "\", \""+c+"\")")

connection.commit()
connection.close()