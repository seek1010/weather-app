# --------------------- Imports ---------------------
import customtkinter as ctk
import requests
import pandas as pd
import threading
import io
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --------------------- Settings ---------------------
API_KEY = "2f4e14f3f42ba00e027d737dff6460fd" 
BASE_URL = "https://api.openweathermap.org/data/2.5/"
ICON_URL = "https://openweathermap.org/img/wn/"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

DEFAULT_CITY = "Dehradun"



# --------------------- API ---------------------
def fetch(endpoint, city):
    try:
        url = f"{BASE_URL}{endpoint}?q={city}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def fetch_icon(icon_code):
    try:
        url = f"{ICON_URL}{icon_code}@2x.png"
        img = requests.get(url, timeout=10).content
        return Image.open(io.BytesIO(img))
    except:
        return None


# --------------------- App ---------------------
class WeatherApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Weather App")
        self.geometry("900x650")
        self.resizable(False, False)

        self.current_icon = None
        self.canvas = None

        self.create_ui()

        self.update_weather_thread()

        

    # --------------------- UI ---------------------
    def create_ui(self):

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(pady=10)

        self.city_entry = ctk.CTkEntry(top, width=250, height=40)
        self.city_entry.insert(0, DEFAULT_CITY)
        self.city_entry.pack(side="left", padx=10)

        self.search_btn = ctk.CTkButton(
            top,
            text="Search",
            command=self.update_weather_thread
        )
        self.search_btn.pack(side="left", padx=5)

        self.theme_btn = ctk.CTkButton(
            top,
            text="Toggle Theme",
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", padx=5)

        # Current weather
        self.city_label = ctk.CTkLabel(self, font=("Segoe UI", 24, "bold"))
        self.city_label.pack()

        self.icon_label = ctk.CTkLabel(self, text="")
        self.icon_label.pack()

        self.temp_label = ctk.CTkLabel(self, font=("Segoe UI", 42))
        self.temp_label.pack()

        self.desc_label = ctk.CTkLabel(self, font=("Segoe UI", 16))
        self.desc_label.pack()

        # Hourly cards
        self.hourly_frame = ctk.CTkFrame(self)
        self.hourly_frame.pack(fill="x", padx=20, pady=10)

        # Plot
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # --------------------- Theme Toggle ---------------------
    def toggle_theme(self):

        current = ctk.get_appearance_mode()

        if current == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    # --------------------- Thread ---------------------
    def update_weather_thread(self):

        threading.Thread(
            target=self.update_weather,
            daemon=True
        ).start()

    # --------------------- Fetch ---------------------
    def update_weather(self):

        city = self.city_entry.get()

        current = fetch("weather", city)
        forecast = fetch("forecast", city)

        if not current or not forecast:
            return

        self.after(
            0,
            lambda: self.update_ui(current, forecast)
        )

    # --------------------- UI Update ---------------------
    def update_ui(self, current, forecast):

        self.city_label.configure(
            text=f"{current['name']}, {current['sys']['country']}"
        )

        self.temp_label.configure(
            text=f"{current['main']['temp']:.1f}°C"
        )

        self.desc_label.configure(
            text=current["weather"][0]["description"].capitalize()
        )

        # Icon
        icon_code = current["weather"][0]["icon"]
        img = fetch_icon(icon_code)

        if img:
            self.current_icon = ctk.CTkImage(img, size=(100, 100))
            self.icon_label.configure(image=self.current_icon)

        # Hourly cards
        self.draw_hourly(forecast)

        # Plot
        self.draw_plot(forecast)

        # Refresh
        #self.refresh_btn = ctk.CTkButton(
        #   top,
        #   text="Refresh",
        #   command=self.update_weather_thread
        #)
        #self.refresh_btn.pack(side="left", padx=5)

    # --------------------- Hourly ---------------------
    def draw_hourly(self, forecast):

        for widget in self.hourly_frame.winfo_children():
            widget.destroy()

        for item in forecast["list"][:6]:

            time = item["dt_txt"][11:16]
            temp = item["main"]["temp"]
            icon = item["weather"][0]["icon"]

            frame = ctk.CTkFrame(self.hourly_frame)
            frame.pack(side="left", padx=5, pady=5)

            img = fetch_icon(icon)

            if img:
                icon_img = ctk.CTkImage(img, size=(40, 40))
                label_icon = ctk.CTkLabel(frame, image=icon_img, text="")
                label_icon.image = icon_img
                label_icon.pack()

            ctk.CTkLabel(frame, text=time).pack()
            ctk.CTkLabel(frame, text=f"{temp:.0f}°C").pack()

    # --------------------- Plot ---------------------
    def draw_plot(self, forecast):

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        data = []

        for item in forecast["list"]:
            data.append({
                "datetime": item["dt_txt"],
                "temp": item["main"]["temp"]
            })

        df = pd.DataFrame(data)
        df["datetime"] = pd.to_datetime(df["datetime"])

        fig = plt.Figure(figsize=(7, 3), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(df["datetime"], df["temp"], marker="o")
        ax.set_title("5-Day Temperature Trend")
        ax.grid(True)

        fig.autofmt_xdate()

        self.canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


# --------------------- Run ---------------------
if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()