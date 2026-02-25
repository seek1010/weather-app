# --------------------- Imports ---------------------
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
import pandas as pd
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --------------------- Settings ---------------------
API_KEY =  "2f4e14f3f42ba00e027d737dff6460fd"   
BASE_URL = "https://api.openweathermap.org/data/2.5/"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DEFAULT_CITY = "Dehradun"


# --------------------- API Function ---------------------
def fetch_weather(endpoint, city):
    try:
        url = f"{BASE_URL}{endpoint}?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        return response.json()
    except:
        return None


# --------------------- Main App ---------------------
class WeatherApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Weather App")
        self.geometry("800x600")
        self.resizable(False, False)

        # Header
        self.header = ctk.CTkLabel(
            self,
            text="Weather Forecast",
            font=("Segoe UI", 28, "bold")
        )
        self.header.pack(pady=15)

        # Search bar
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(pady=10)

        self.city_entry = ctk.CTkEntry(
            self.search_frame,
            width=300,
            height=40,
            font=("Segoe UI", 14),
            placeholder_text="Enter city"
        )
        self.city_entry.pack(side="left", padx=10)
        self.city_entry.insert(0, DEFAULT_CITY)

        self.search_btn = ctk.CTkButton(
            self.search_frame,
            text="Search",
            width=120,
            height=40,
            command=self.update_weather_thread
        )
        self.search_btn.pack(side="left")

        # Current weather
        self.city_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 22, "bold"))
        self.city_label.pack(pady=5)

        self.temp_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 48))
        self.temp_label.pack()

        self.desc_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 16))
        self.desc_label.pack()

        self.stats_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 14))
        self.stats_label.pack(pady=10)

        # Plot area
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = None

        # Initial load
        self.update_weather_thread()

    # --------------------- Thread wrapper ---------------------
    def update_weather_thread(self):
        threading.Thread(target=self.update_weather, daemon=True).start()

    # --------------------- Main weather update ---------------------
    def update_weather(self):

        city = self.city_entry.get().strip()

        if not city:
            messagebox.showwarning("Input Error", "Enter city name")
            return

        current = fetch_weather("weather", city)
        forecast = fetch_weather("forecast", city)

        if not current or not forecast:
            messagebox.showerror("Error", "Could not fetch weather")
            return

        # Update UI safely
        self.after(0, lambda: self.update_ui(current, forecast))

    # --------------------- UI Update ---------------------
    def update_ui(self, current, forecast):

        # Current weather
        self.city_label.configure(
            text=f"{current['name']}, {current['sys']['country']}"
        )

        self.temp_label.configure(
            text=f"{current['main']['temp']:.1f}°C"
        )

        self.desc_label.configure(
            text=f"{current['weather'][0]['description'].capitalize()}"
        )

        # Forecast processing
        data = []

        for item in forecast["list"]:
            data.append({
                "datetime": item["dt_txt"],
                "temp": item["main"]["temp"]
            })

        df = pd.DataFrame(data)
        df["datetime"] = pd.to_datetime(df["datetime"])

        avg = df["temp"].mean()
        mx = df["temp"].max()

        self.stats_label.configure(
            text=f"5-Day Avg: {avg:.1f}°C   Max: {mx:.1f}°C"
        )

        self.draw_plot(df)

    # --------------------- Plot ---------------------
    def draw_plot(self, df):

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        fig = plt.Figure(figsize=(7, 3), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(df["datetime"], df["temp"], marker="o")
        ax.set_title("Temperature Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature °C")
        ax.grid(True)

        fig.autofmt_xdate()

        self.canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


# --------------------- Run ---------------------
if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()