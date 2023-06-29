import pandas as pd
from collections import OrderedDict
# xls = pd.ExcelFile('ValidationAppWeb/resources/human_validation.csv')
# df = pd.read_excel(xls, 'New Label Tree')[['2nd level', '3rd level',  '4th level']]
df = pd.read_csv('ValidationAppWeb/serverSide/old_mpii_human_pose_v1_u12_1.csv')
df.sort_values(by="cat_name", inplace=True)


categories_DB = {}

for idx, row in df.iterrows():
    if not(row[2] in categories_DB):
        categories_DB[row[2]] = []
        if not (row[3] in categories_DB[row[2]]):
            categories_DB[row[2]].append(row[3])
    else:
        if not(row[3] in categories_DB[row[2]]):
            categories_DB[row[2]].append(row[3])
    
for item in categories_DB.keys():
    categories_DB[item].sort(reverse=False)

import json
with open("ValidationAppWeb/resources/categories.json", "w") as fp:
    # print(categories_DB)
    json.dump(categories_DB, fp)
    # print(sorted.keys())