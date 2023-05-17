import pandas as pd
# xls = pd.ExcelFile('ValidationAppWeb/resources/human_validation.csv')
# df = pd.read_excel(xls, 'New Label Tree')[['2nd level', '3rd level',  '4th level']]
df = pd.read_csv('ValidationAppWeb/resources/old_mpii_human_pose_v1_u12_1.csv')

categories_DB = {}

for idx, row in df.iterrows():
    if not(row[3] in categories_DB):
        categories_DB[row[3]] = []
        if not (row[4] in categories_DB[row[3]]):
            categories_DB[row[3]].append(row[4])
    else:
        if not(row[4] in categories_DB[row[3]]):
            categories_DB[row[3]].append(row[4])

import json
with open("ValidationAppWeb/resources/categories.json", "w") as fp:
    json.dump(categories_DB,fp)
