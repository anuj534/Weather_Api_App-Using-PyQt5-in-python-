import os
import sys
import requests
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt 

load_dotenv()

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name:", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.initUI()
    
    
    def initUI(self):
        self.setWindowTitle("Weather App")
        vbox = QVBoxLayout()
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")
        
        self.setStyleSheet("""
                QWidget {
                    background-color: #0f172a;
                    color: #f8fafc;
                    font-family: Calibri, "Segoe UI", sans-serif;
                }

                QLabel#city_label {
                    font-size: 40px;
                    font-style: italic;
                    color: #94a3b8;
                    margin-bottom: 5px;
                }

                QLineEdit#city_input {
                    font-size: 40px;
                    background-color: #1e293b;
                    color: #ffffff;
                    border: 2px solid #334155;
                    border-radius: 15px;
                    padding: 10px 20px;
                }

                QLineEdit#city_input:focus {
                    border: 2px solid #38bdf8;
                    background-color: #1e293b;
                }

                QPushButton#get_weather_button {
                    font-size: 30px;
                    font-weight: bold;
                    color: #0f172a;
                    background-color: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #38bdf8, 
                        stop: 1 #818cf8
                    );
                    border: none;
                    border-radius: 15px;
                    padding: 15px 30px;
                    margin-top: 10px;
                }

                QPushButton#get_weather_button:hover {
                    background-color: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #7dd3fc, 
                        stop: 1 #a5b4fc
                    );
                }

                QPushButton#get_weather_button:pressed {
                    background-color: #0284c7;
                    color: #ffffff;
                    padding-top: 17px;
                    padding-bottom: 13px;
                }

                QLabel#temperature_label {
                    font-size: 75px;
                    font-weight: bold;
                    color: #ffffff;
                    margin-top: 15px;
                }

                QLabel#emoji_label {
                    font-size: 100px;
                    font-family: "Segoe UI Emoji";
                }

                QLabel#description_label {
                    font-size: 50px;
                    color: #cbd5e1;
                }
            """)


        self.get_weather_button.clicked.connect(self.get_weather)
        

    def get_weather(self):
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            self.display_error("API key missing:\nAdd it to your .env file")
            return
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}" 

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data["cod"] == 200:
                  self.display_weather(data)
        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API Key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not Found:\nCity is not found")
                case 500:
                    self.display_error("Inertnal Server Error:\nPlease try again late")
                case 502:
                    self.display_error("Bad Gateway:\nInvalid response from server")
                case 503:
                    self.display_error("Service Unavaiblable:\nServer is down")
                case 504:
                    self.display_error("Gateway Timeout:\nNo response from the server")
                case _:
                    self.display_error(f"HTTP error occuried:\n{http_error}")
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the url")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")
        

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]
        self.temperature_label.setText(f"{temperature_c:.0f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(f"{weather_description}")

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <=232:
            return "⛈️"
        elif 300<= weather_id <= 321:
            return "⛅"
        elif 500<= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <=622:
            return "❄️"
        elif 701 <= weather_id <=741:
            return "🌫️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "🌞"
        elif 801<= weather_id <= 804:
            return "☁️"
        else:
            return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
