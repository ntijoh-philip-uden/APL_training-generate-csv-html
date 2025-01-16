import ray
import os
import csv

ray.init()

directory_name = 'outputs'

try:
    os.makedirs(directory_name)
    print(f"Directory '{directory_name}' created.")
except FileExistsError:
    print(f"Directory '{directory_name}' already exists.")
except PermissionError:
    print(f"Permission denied: Unable to create '{directory_name}'.")

@ray.remote
def create_html_file(directory_name):
    html_file_path = os.path.join(directory_name, "results.html")
    with open(html_file_path, "w") as html_file:
        html_file.write("funkar detta verkligen?")
    print(f"HTML file created at {html_file_path}")

@ray.remote
def create_csv_file(directory_name):
    csv_file_path = os.path.join(directory_name, "results.csv")
    with open(csv_file_path, "w", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Column1", "Column2", "Column3"])
        csv_writer.writerow(["Data1", "Data2", "Data3"])
    print(f"CSV file created at {csv_file_path}")

# Run tasks in parallel
ray.get([create_html_file.remote(directory_name), create_csv_file.remote(directory_name)])