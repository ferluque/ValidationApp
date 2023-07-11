import sqlite3 as sql
import pandas as pd
import sys
import datetime
import random
import json

if (len(sys.argv)!=2):
    print("Error: pytnon randomValidator.py <path_to_csv>")
    exit(-1)
    
with open('static/categories.json') as file:
    data = json.load(file)
    
# print(data)
    
connection = sql.connect("validation.db")
cur = connection.cursor()
cur.execute("pragma foreign_keys=ON")

file = pd.read_csv(sys.argv[1])

keys = list(data.keys())

# print(file)

for i in range(len(file.index)):
    rnd = random.randint(0, len(keys)-1)
    file.at[i, 'cat_name'] = keys[rnd]
    rnd2 = random.randint(0, len(data[keys[rnd]])-1)
    file.at[i, 'act_name'] = data[keys[rnd]][rnd2]   
    

# print(file)
file['model'] = pd.Series(['RandomValidator' for x in range(len(file.index))])
# file['priority'] = pd.Series([4 for x in range(len(file.index))])
# file['timestamp'] = pd.Series([str(datetime.datetime.now()) for x in range(len(file.index))])
# file['ignored'] = pd.Series([0 for x in range(len(file.index))])
file = file.values.tolist()

# print(file)
cur.executemany("INSERT INTO modelOutput VALUES(?, ?, ?, ?)", file)
# cur.executemany("INSERT INTO validation VALUES(?, ?, ?, ?, ?, ?, ?)", file)
connection.commit()