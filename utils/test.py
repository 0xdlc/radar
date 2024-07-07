import os
import numpy as np
# Define the directory path to start iterating from
directory_path = '/home/madvillain/Documents/code/pythons/radarenv/output'

# Function to iterate through directories and read files
def iterate_directories(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            print(file_path)
            #print(content)
            print("--------------------------------------")

# Call the function with the specified directory path
iterate_directories(directory_path)

