import sqlite3 as sql
import pandas as pd
import sys
import datetime

if (len(sys.argv)<3):
    print("Error: pytnon insertCSVResults.py <path_to_csv> <model_name>")
    exit(-1)

connection = sql.connect("validation.db")
cur = connection.cursor()
cur.execute("pragma foreign_keys=ON")

file = pd.read_csv(sys.argv[1])

file['model'] = pd.Series([sys.argv[2] for x in range(len(file.index))])

# file['username'] = pd.Series([sys.argv[2] for x in range(len(file.index))])
# file['priority'] = pd.Series([4 for x in range(len(file.index))])
# file['timestamp'] = pd.Series([str(datetime.datetime.now()) for x in range(len(file.index))])
# file['ignored'] = pd.Series([0 for x in range(len(file.index))])
file = file.values.tolist()

print(file)
cur.executemany("INSERT INTO modelOutput VALUES(?, ?, ?, ?)", file)
# cur.executemany("INSERT INTO validation VALUES(?, ?, ?, ?, ?, ?, ?)", file)
connection.commit()

# for _,f, a, c, _ in file:
#     insert = "insert into modelOutput (file_name, level1, level2, model) values ('{filename}','{level1}','{level2}','{model}')".format(
#         filename=f, level1=a, level2=c, model=sys.argv[2])
#     print(insert)
#     cur.execute(insert)

# connection.commit()
# connection.close()