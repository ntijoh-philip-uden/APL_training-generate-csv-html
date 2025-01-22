import ray
import os
import csv
import requests
import datetime
import matplotlib.pyplot as plt

ray.init()

directory_name = 'outputs'
img_directory_name = os.path.join(directory_name, 'img')

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

# Your WeatherAPI key
API_KEY = '6b20f3c4270947378aa113121252101'
BASE_URL = 'http://api.weatherapi.com/v1/current.json'

# City to get the weather for
city = 'Gothenburg'

# Build the request URL
url = f"{BASE_URL}?key={API_KEY}&q={city}"

# Make the GET request
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

# Parse the JSON response
weather_data = response.json()

# Extract desired information
temp_c = weather_data['current']['temp_c']
condition = weather_data['current']['condition']['text']
print(f"The current temperature in {city} is {temp_c}°C with {condition}.")
location = weather_data['location']['name']
country = weather_data['location']['country']
wind_kph = weather_data['current']['wind_kph']
humidity = weather_data['current']['humidity']

# Generate a Matplotlib diagram
def create_weather_plot():
    labels = ['Temperature (°C)', 'Wind Speed (kph)', 'Humidity (%)']
    values = [temp_c, wind_kph, humidity]
    
    # 1. Bar Chart
    plt.figure(figsize=(6, 6))
    colors = ['blue' if temp_c < 0 else 'red', 'orange', 'green']
    plt.bar(labels, values, color=colors)
    plt.title(f"Bar Chart: Weather Data for {location}, {country}")
    plt.ylabel("Values")
    plt.savefig(os.path.join(img_directory_name, "bar_chart.png"))
    plt.close()

    # 2. Line Graph
    plt.figure(figsize=(6, 4))
    plt.plot(labels, values, marker='o', color='purple', linestyle='--')
    plt.title(f"Line Graph: Weather Data for {location}, {country}")
    plt.ylabel("Values")
    plt.savefig(os.path.join(img_directory_name, "line_graph.png"))
    plt.close()

    print("All weather plots saved.")

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
            <h1>Weather Data for {location}, {country}</h1>
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
def create_csv_file(directory_name):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [current_time, location, country, temp_c, condition, wind_kph, humidity]  # Weather data
    
    csv_file_path = os.path.join(directory_name, "results.csv")
    with open(csv_file_path, "a", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        if csv_file.tell() == 0:
            csv_writer.writerow(["Time", "Location", "Country", "Temperature (°C)", "Condition", "Wind Speed (kph)", "Humidity (%)"])
        csv_writer.writerow(data)
    print(f"CSV file created at {csv_file_path}")

# Run tasks in parallel
ray.get([create_html_file.remote(directory_name), create_csv_file.remote(directory_name)])
