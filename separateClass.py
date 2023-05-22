import os
import subprocess
import sys
import math
import shutil
import time
import csv
from call_function_with_timeout import SetTimeout

if (len(sys.argv)!=2):
    print("Error: python copyImages.py <class_to_select>")
    exit
   
print("Removing existing files")
dest = '/var/www/nas_storage/outputs_parques_nacionales'
try:
    shutil.rmtree(os.path.join(dest, 'separated', sys.argv[1]))
except:
    print("Not existing")
os.makedirs(os.path.join(dest, 'separated', sys.argv[1]), exist_ok=True) 

copy_with_timeout = SetTimeout(shutil.copyfile, timeout=30)

for file in os.listdir():
    if file.endswith('.csv'):
        print("\nWorking on ", file)
        csv_file = file
        selected_class = sys.argv[1]

        # source = "C:\\Users\\fl156\\Desktop\\TFG\\ValidationApp"
        # dest = "C:\\Users\\fl156\\Desktop\\TFG\\ValidationApp"

        dest = '/var/www/nas_storage/outputs_parques_nacionales'
        csv_file = os.path.join(dest, csv_file)
        source = '/var/www/nas_storage/Imagenes_parques_nacionales'
        dest = os.path.join(dest, 'separated')
        dest = os.path.join(dest, selected_class)
        # dir = os.listdir(source)

        # Leemos csv
        file = open(csv_file, 'r')
        data = list(csv.reader(file, delimiter=','))
        data = data[1:]
        toolbar_width = 50
        
        for i, row in enumerate(data,start=1):
            filename = row[0].split('\\')[2:]
            if (row[2]==selected_class):
                path = source
                if (filename[0]=='Flickr'):
                    path = os.path.join(source,'Flickr_all')
                    for a in filename[1:]:
                        path = os.path.join(path, a)
                else:
                    path = os.path.join(source,'Twitter_all')
                    for a in filename[1:]:
                        path = os.path.join(path, a)
                
                try:
                    _,timeout, _,_ = copy_with_timeout(path, os.path.join(dest, filename[len(filename)-1]))                 
                # If source and destination are same
                except shutil.SameFileError:
                    print("\nSource and destination represents the same file.")                 
                # If there is any permission issue
                except PermissionError:
                    print("\nPermission denied.")                 
                # For other errors
                except Exception as e:
                    print("\nError: ", e)
                # shutil.copyfile(path, os.path.join(dest, row[0].split('\\')[len(row[0].split('\\'))-1]))
                if timeout:
                    print("Timeout on img: ", filename[len(filename)-1])

            perc = (i+1) / len(data)
            current_progress = int(math.ceil(perc * toolbar_width))
            print('\r' ,'#' * current_progress, '-' * (toolbar_width - current_progress), round(perc * 100, 2), '%',
                 end='')
print("Finished class: ", selected_class)
