import pandas as pd
import os

df = pd.read_csv('modelsResultsInsert/human_validation.csv')

images = df['file_name'].values.tolist()

imgs = os.listdir('static/images')

for img in imgs:
    if img not in images:
        os.remove('static/images/'+img)