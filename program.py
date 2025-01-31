import ray
import os
import csv
import requests
import datetime
import matplotlib.pyplot as plt
import subprocess
import json

ray.init()

# Directory setup
directory_name = 'outputs'
img_directory_name = os.path.join(directory_name, 'img')

# Ensure directories exist
try:
    os.makedirs(directory_name)
    print(f"Directory '{directory_name}' created.")
except FileExistsError:
    print(f"Directory '{directory_name}' already exists.")
except PermissionError:
    print(f"Permission denied: Unable to create '{directory_name}'.")

try:
    os.makedirs(img_directory_name)
    print(f"Directory '{img_directory_name}' created.")
except FileExistsError:
    print(f"Directory '{img_directory_name}' already exists.")
except PermissionError:
    print(f"Permission denied: Unable to create '{img_directory_name}'.")

# Weather API setup
API_KEY = '6b20f3c4270947378aa113121252101'
BASE_URL = 'http://api.weatherapi.com/v1/current.json'
city = str(input("Ange en stad: "))
url = f"{BASE_URL}?key={API_KEY}&q={city}"

response = requests.get(url)
if response.status_code == 200:
    print("Success!")
elif response.status_code == 400:
    print("Bad request! Check your parameters.")
    raise SystemExit
elif response.status_code == 403:
    print("Unauthorized! Check your API key.")
    raise SystemExit
elif response.status_code == 404:
    print("Not found! Check your BASE_URL.")
    raise SystemExit
else:
    print(f"Error: {response.status_code}")
    raise SystemExit

weather_data = response.json()
temp_c = weather_data['current']['temp_c']
condition = weather_data['current']['condition']['text']
location = weather_data['location']['name']
country = weather_data['location']['country']
wind_kph = weather_data['current']['wind_kph']
humidity = weather_data['current']['humidity']
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Plot weather data
def create_weather_plot():
    labels = ['Temperature (°C)', 'Wind Speed (kph)', 'Humidity (%)']
    values = [temp_c, wind_kph, humidity]

    # Bar chart
    plt.figure(figsize=(6, 6))
    colors = ['blue' if temp_c < 0 else 'red', 'orange', 'green']
    plt.bar(labels, values, color=colors)
    plt.title(f"Weather Data: {location}, {country}")
    plt.savefig(os.path.join(img_directory_name, "bar_chart.png"))
    plt.close()

    # Line graph
    plt.figure(figsize=(6, 4))
    plt.plot(labels, values, marker='o', color='purple')
    plt.title(f"Weather Data: {location}, {country}")
    plt.savefig(os.path.join(img_directory_name, "line_graph.png"))
    plt.close()

    print("Weather plots saved.")

create_weather_plot()

@ray.remote
def create_html_file(directory_name):
    html_file_path = os.path.join(directory_name, "results.html")
    with open(html_file_path, "w") as html_file:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Weather Report</title>
        </head>
        <body>
            <h1>Weather Data for {location}, {country} {current_time}</h1>
            <p><strong>Temperature:</strong> {temp_c}°C</p>
            <p><strong>Condition:</strong> {condition}</p>
            <p><strong>Wind Speed:</strong> {wind_kph} kph</p>
            <p><strong>Humidity:</strong> {humidity}%</p>
            <h2>Weather Charts</h2>
            <h3>Bar Chart</h3>
            <img src="img/bar_chart.png" alt="Bar Chart of Weather Data">
            <h3>Line Graph</h3>
            <img src="img/line_graph.png" alt="Line Graph of Weather Data">
        </body>
        </html>
        """
        html_file.write(html_content)
    print(f"HTML file created at {html_file_path}")

@ray.remote
def create_csv_file(directory_name, choice, num_records):
    try:
        user_input = f"{choice}\n{num_records}\n"
        generator_process = subprocess.Popen(
            ["python3.11", "genuserscript.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="scripts"  # Set the working directory to "scripts"
        )
        stdout, stderr = generator_process.communicate(input=user_input)

        if generator_process.returncode != 0:
            print(f"Error in generator script: {stderr}")
            return

        data = json.loads(stdout)

        csv_file_path = os.path.join(directory_name, "results.csv")
        with open(csv_file_path, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Define CSV header based on user choice
            csv_writer.writerow(["name"] + (["email"] if choice >= 1 else []) + (["age"] if choice >= 2 else []) + (["phone"] if choice >= 3 else []))
            csv_writer.writerows([[record["name"]] + ([record["email"]] if choice >= 1 else []) + ([record.get("age", "")] if choice >= 2 else []) + ([record.get("phone", "")] if choice >= 3 else []) for record in data])
        print(f"CSV file created at {csv_file_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Vad för slags data vill du generera?")
    print("1. Namn och email")
    print("2. Namn, email och ålder")
    print("3. Namn, email, ålder och telefonnummer")

    choice = int(input("Ange ett val (1/2/3): "))
    num_records = int(input("Hur många dataposter vill du generera? "))

    ray.get([
        create_html_file.remote(directory_name),
        create_csv_file.remote(directory_name, choice, num_records)
    ])
