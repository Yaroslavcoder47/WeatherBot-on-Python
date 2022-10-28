import telebot
from telebot import types
import requests
from config import (token, url_weather_minsk, url_weather_grodno, url_weather_brest, url_weather_gomel,
                    url_weather_mogilev, url_weather_vitebsk, agent)
from bs4 import BeautifulSoup


bot = telebot.TeleBot(token)


city_dict = {"Minsk": url_weather_minsk, "Grodno": url_weather_grodno, "Brest": url_weather_brest,
             "Gomel": url_weather_gomel, "Mogilev": url_weather_mogilev, "Vitebsk": url_weather_vitebsk}
chat = 1480135859


class WeatherData:
    def __init__(self, weather):
        self.WEATHER = weather
    headers = {'User-Agent': agent}

    def get_temperature(self):
        full_page = requests.get(self.WEATHER, headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        try:
            convert = soup.findAll("span", {"class": "value"})
            return convert[0].text
        except IndexError:
            bot.send_message(chat, "Something went wrong😢. Please try again.", parse_mode='html')

    def get_felt_temperature(self):
        full_page = requests.get(self.WEATHER, headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        try:
            convert = soup.findAll("span", {"class": "value colorize-server-side"})
            return convert[0].text
        except IndexError:
            bot.send_message(chat, "Something went wrong😢. Please try again.", parse_mode='html')

    def get_wind(self):
        full_page = requests.get(self.WEATHER, headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        try:
            convert = soup.findAll("div", {"class": "h5 margin-bottom-0"})
            return convert[0].text
        except IndexError:
            bot.send_message(chat, "Something went wrong😢. Please try again.", parse_mode='html')

    def get_humidity(self):
        full_page = requests.get(self.WEATHER, headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        try:
            convert = soup.findAll("div", {"class": "h5 margin-bottom-0"})
            return convert[1].text
        except IndexError:
            bot.send_message(chat, "Something went wrong😢. Please try again.", parse_mode='html')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    weather_button = types.KeyboardButton("Weather")
    chat = message.chat.id
    markup.add(weather_button)
    bot.send_message(chat, f"Hello <b>{message.from_user.first_name}</b> this is WeatherBot "
                                      f"which can help you to find weather in your region",
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_weather_data(message):
    if message.chat.type == 'private':
        if message.text == 'Weather':
            markup = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "You have an opportunity to choose a city", parse_mode='html',
                             reply_markup=markup)
            markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            city1 = types.KeyboardButton("Minsk")
            city2 = types.KeyboardButton("Grodno")
            city3 = types.KeyboardButton("Brest")
            city4 = types.KeyboardButton("Gomel")
            city5 = types.KeyboardButton("Mogilev")
            city6 = types.KeyboardButton("Vitebsk")
            markup1.add(city1, city2, city3, city4, city5, city6)
            bot.send_message(message.chat.id, "Please, choose a city", reply_markup=markup1)
        city_list = ['Minsk', 'Mogilev', 'Grodno', 'Brest', 'Gomel', 'Vitebsk']
        if message.text in city_list:
            city_url = city_dict[message.text]
            temp = WeatherData(city_url).get_temperature()
            felt_temp = WeatherData(city_url).get_felt_temperature()
            wind = WeatherData(city_url).get_wind()
            try:
                speed = str(wind[5:14])
                wind_str = ""
                if wind[0] == 'W':
                    wind_str = 'West'
                elif wind[0] == 'E':
                    wind_str = 'East'
                elif wind[0] == 'S':
                    wind_str = 'South'
                    if wind[1] == 'E':
                        wind_str += '-East'
                    elif wind[1] == 'W':
                        wind_str += "-West"
                elif wind[0] == 'N':
                    wind_str = 'North'
                    if wind[1] == 'E':
                        wind_str += '-East'
                    elif wind[1] == 'W':
                        wind_str += "-West"
                humidity = WeatherData(city_url).get_humidity()
                if int(humidity[0:2]) <= 40:
                    temp += "☀"
                elif (int(humidity[0:2]) >= 40) and (int(humidity[0:2]) <= 95):
                    temp += "⛅"
                elif int(humidity[0:2]) >= 95 or int(humidity[0:3] == 100):
                    temp += "🌧"
                bot.send_message(message.chat.id, f"Temperature {str(temp)}. Felt as {str(felt_temp)}." +
                                 "\n" + f"Wind: {str(wind_str)}. Speed: {str(speed)}",
                                 parse_mode='html')
            except:
                bot.send_message(message.chat.id, "Something went wrong😢. Please try again.", parse_mode='html')


bot.polling(none_stop=True)
