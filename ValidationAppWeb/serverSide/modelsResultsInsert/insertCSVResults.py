import sqlite3 as sql
import pandas as pd
import sys

if (len(sys.argv)<3):
    print("Error: pytnon insertCSVResults.py <path_to_csv> <model_name>")
    exit(-1)

connection = sql.connect("../validation.db")
cur = connection.cursor()
cur.execute("pragma foreign_keys=ON")

file = pd.read_csv(sys.argv[1]).values.tolist()
print(file[0])

for _,_,f, a, c in file:
    cur.execute("insert into modelOutput (file_name, level1, level2, model) values ('{filename}','{level1}','{level2}','{model}')".format(
        filename=f, level1=a, level2=c, model=sys.argv[2]
    ))

connection.commit()
connection.close()