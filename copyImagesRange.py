import os
import subprocess
import sys
import shutil
import math
import csv

if (len(sys.argv) != 5):
    print("Error: python copyImagesRange.py <csv_to_read> <class_to_select> <min> <max>")

csv_file = sys.argv[1]
selected_class = sys.argv[2]
minimum = int(sys.argv[3])
maximum = int(sys.argv[4])

dest = os.getcwd()
csv_file = os.path.join(dest, csv_file)
dest = os.path.join(dest, 'separated', selected_class)
os.makedirs(dest, exist_ok=True)
# Leemos csv
file = open(csv_file, 'r')
data = list(csv.reader(file, delimiter=','))
file.close()
maximum = min(maximum, len(data))
data = data[minimum : maximum]

source = '/var/www/nas_storage/Imagenes_parques_nacionales'
toolbar_width = 50
for i, row in enumerate(data):
    filename = row[0].split('\\')[2:]
    if (row[2] == selected_class):
        path = source
        for a in filename:
            path = os.path.join(path, a)
        shutil.copyfile(path, os.path.join(dest, filename[len(filename) - 1]))

    perc = (i + 1) / (maximum-minimum)
    current_progress = int(math.ceil(perc * toolbar_width))
    print('\r', '#' * current_progress, '-' * (toolbar_width - current_progress), round(perc * 100, 2), '%',
          end='')
