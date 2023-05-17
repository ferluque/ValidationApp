import os
import subprocess
import sys

if (len(sys.argv)!=3):
    print("Error: python copyImages.py <csv_to_read> <class_to_select>")

csv_file = sys.argv[1]
selected_class = sys.argv[2]

# source = "C:\\Users\\fl156\\Desktop\\TFG\\ValidationApp"
# dest = "C:\\Users\\fl156\\Desktop\\TFG\\ValidationApp"

source = os.getcwd()
dest = os.getcwd()
dest = os.path.join(dest, selected_class)
# dir = os.listdir(source)

# Leemos csv
import csv
file = open(csv_file, 'r')
data = list(csv.reader(file, delimiter=','))
data = data[1:]

for i, row in enumerate(data,start=1):
    filename = row[0].split('\\')[2:]
    if (row[2]==selected_class):
        if (filename[0]=='Flickr'):
            path = os.path.join(source,'Flickr_all')
            for a in row[1:]:
                path = os.path.join(path, a)
        else:
            path = os.path.join(source,'Twitter_all')
            for a in row[1:]:
                path = os.path.join(path, a)
        import shutil
        shutil.copyfile(path, os.path.join(dest, row[0].split('\\')[len(row[0].split('\\'))-1]))