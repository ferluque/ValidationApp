import pandas as pd
import sqlite3

connection = sqlite3.connect("validation.db", check_same_thread=False)
cur = connection.cursor()
cur.execute("pragma foreign_keys=ON")

df = pd.read_csv('modelsResultsInsert/human_validation.csv')

images = df['file_name'].values.tolist()

for image in images:
    cur.execute("insert into images (file_name) values ('{image}')".format(image=image))
    
connection.commit()