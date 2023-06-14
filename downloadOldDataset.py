import pandas as pd
import requests
df = pd.read_csv('OldDataset/oldDataset.csv')

for url in df['url_o']:
    r = requests.get(url, allow_redirects=True)
    split = url.split('/')
    filename = split[len(split)-1].removesuffix('?zz=1')
    # print(filename)
    open('OldDataset/images/'+filename, 'wb').write(r.content)