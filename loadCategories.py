import pandas as pd
xls = pd.ExcelFile('CESLabelsTree_asv_march2023.xlsx')
df = pd.read_excel(xls, 'New Label Tree')[['2nd level', '3rd level',  '4th level']]

categories_DB = {}

for idx, row in df.iterrows():
    if not(row[0] in categories_DB):
        categories_DB[row[0]] = {}
        categories_DB[row[0]][row[1]] = []
        if not (row[2] in categories_DB[row[0]][row[1]]):
            if not(pd.isna(row[2])):
                categories_DB[row[0]][row[1]].append(row[2])
    else:
        if not(row[1] in categories_DB[row[0]]):
            categories_DB[row[0]][row[1]] = []
        if not (row[2] in categories_DB[row[0]][row[1]]):
            if not(pd.isna(row[2])):
                categories_DB[row[0]][row[1]].append(row[2])
import json
with open("Categories\\CESLabelsTreeDict.json", "w") as fp:
    json.dump(categories_DB,fp)
