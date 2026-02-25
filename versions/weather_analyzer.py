

# --------------------- Your settings ---------------------
        
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json  

# --------------------- Settings ---------------------
API_KEY = "2f4e14f3f42ba00e027d737dff6460fd"        
BASE_URL = "https://api.openweathermap.org/data/2.5/"
ctk.set_appearance_mode("Dark")      # "Light", "Dark" or "System"
ctk.set_default_color_theme("blue")    # "blue", "dark-blue", "green"

CITY = "Dehradun"  

# --------------------- Fetch Functions ---------------------
def fetch_current(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code != 200:
            messagebox.showerror("Error", data.get("message", "City not found"))
            return None
        return data
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))
        return None

def fetch_forecast(city):
    url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if resp.status_code != 200:
            return None
        return data
    except:
        return None

# --------------------- GUI Class ---------------------
class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Weather Forecast")
        self.geometry("780x620")
        self.resizable(False, False)

        # Header
        self.header = ctk.CTkLabel(self, text="Weather Forecast", font=("Segoe UI", 24, "bold"))
        self.header.pack(pady=(20, 10))

        # City input + button
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=10)

        self.city_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter city (e.g. Pune)", width=280, height=40, font=("Segoe UI", 14))
        self.city_entry.pack(side="left", padx=10)
        self.city_entry.insert(0, CITY)  # Default value

        self.search_btn = ctk.CTkButton(self.input_frame, text="Search", width=120, height=40, command=self.update_weather)
        self.search_btn.pack(side="left")

        # Main content area (tabs)
        self.tabview = ctk.CTkTabview(self, width=720, height=420)
        self.tabview.pack(pady=15, padx=20)
        self.tabview.add("Current")
        self.tabview.add("Forecast")

        # Current weather labels (will be updated)
        self.current_frame = ctk.CTkFrame(self.tabview.tab("Current"), fg_color="transparent")
        self.current_frame.pack(expand=True, pady=20)

        self.city_label = ctk.CTkLabel(self.current_frame, text="", font=("Segoe UI", 20, "bold"))
        self.city_label.pack(pady=5)

        self.temp_label = ctk.CTkLabel(self.current_frame, text="", font=("Segoe UI", 48))
        self.temp_label.pack(pady=5)

        self.feels_like = ctk.CTkLabel(self.current_frame, text="", font=("Segoe UI", 16))
        self.feels_like.pack()

        self.humidity_desc = ctk.CTkLabel(self.current_frame, text="", font=("Segoe UI", 16))
        self.humidity_desc.pack(pady=8)

        # Forecast tab - will hold stats + plot
        self.forecast_frame = ctk.CTkFrame(self.tabview.tab("Forecast"), fg_color="transparent")
        self.forecast_frame.pack(expand=True, fill="both", pady=10, padx=10)

        self.stats_label = ctk.CTkLabel(self.forecast_frame, text="Forecast Stats will appear here", font=("Segoe UI", 14))
        self.stats_label.pack(pady=10)

        # Placeholder for matplotlib plot
        self.canvas = None

        # Initial load
        self.update_weather()

    def update_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input", "Please enter a city")
            return

        current = fetch_current(city)
        forecast = fetch_forecast(city)

        if current:
            self.city_label.configure(text=f"{current['name']}, {current['sys']['country']}")
            self.temp_label.configure(text=f"{current['main']['temp']:.1f} °C")
            self.feels_like.configure(text=f"Feels like {current['main']['feels_like']:.1f} °C • {current['weather'][0]['description'].capitalize()}")
            self.humidity_desc.configure(text=f"Humidity: {current['main']['humidity']}% • Pressure: {current['main']['pressure']} hPa")

        if forecast and 'list' in forecast:
            # Build DataFrame (same as your old code)
            data = []
            for item in forecast['list']:
                data.append({
                    'datetime': item['dt_txt'],
                    'temp': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'desc': item['weather'][0]['description']
                })

            df = pd.DataFrame(data)
            df['datetime'] = pd.to_datetime(df['datetime'])

            # Stats
            avg_temp = df['temp'].mean()
            max_temp = df['temp'].max()
            self.stats_label.configure(text=f"5-Day Forecast • Avg: {avg_temp:.1f}°C • Max: {max_temp:.1f}°C")

            # Daily averages
            df['date'] = df['datetime'].dt.date
            daily = df.groupby('date')['temp'].mean().round(1)
            daily_text = "\n".join([f"{d}: {t}°C" for d, t in daily.items()])
            self.stats_label.configure(text=f"{self.stats_label.cget('text')}\n\nDaily Averages:\n{daily_text}")

            # Plot (embed in GUI)
            self.draw_plot(df)

    def draw_plot(self, df):
        # Clear previous plot if exists
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        fig = plt.Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(df['datetime'], df['temp'], marker='o', color="#1e88e5", linewidth=2, markersize=6)
        ax.set_title("Temperature Trend (Next 5 Days)", fontsize=14, pad=10)
        ax.set_xlabel("Time", fontsize=11)
        ax.set_ylabel("Temperature (°C)", fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.tick_params(axis='x', rotation=35)

        self.canvas = FigureCanvasTkAgg(fig, master=self.forecast_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

# --------------------- Run the app ---------------------
# --------------------- Run the app ---------------------
if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()