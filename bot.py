import telebot
import requests
from telebot import types

import telebot
import requests
from config import TOKEN

# токен в файле с настройками
API_TOKEN = TOKEN
bot = telebot.TeleBot(API_TOKEN)

# ключ от openweathermap
WEATHER_API_KEY = '42e350199fc9e564dfdb2eb21e3c540e'

# создаём клавиатуру с кнопками
def get_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # делаем кнопки поменьше
    
    # кнопка для отправки геолокации
    btn_geo = types.KeyboardButton("Моя геопозиция", request_location=True)
    
    # кнопка с информацией о проекте
    btn_about = types.KeyboardButton("О проекте")
    
    # добавляем обе кнопки
    markup.add(btn_geo, btn_about)
    return markup

# функция для запроса погоды по координатам
def get_weather(lat, lon):
    # собираем ссылку для запроса к апи погоды
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    
    try:
        # отправляем запрос
        response = requests.get(url)
        data = response.json()  # превращаем ответ в словарь
        
        if response.status_code == 200:  # если всё хорошо достаём нужные данные из ответа
            city = data['name']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            
            # выбираем эмодзи в зависимости от погоды
            emoji = "🌤️"  # стандартная иконка
            desc_lower = description.lower()  # приводим к нижнему регистру для сравнения
            
            # проверяем разные варианты погоды
            if "ясно" in desc_lower or "солнце" in desc_lower:
                emoji = "☀️"  # солнце
            elif "облачно" in desc_lower or "пасмурно" in desc_lower:
                emoji = "☁️"  # облачко
            elif "дождь" in desc_lower or "ливень" in desc_lower:
                emoji = "🌧️"  # дождик
            elif "снег" in desc_lower:
                emoji = "❄️"  # снежинка
            elif "гроза" in desc_lower:
                emoji = "⛈️"  # гроза
            elif "туман" in desc_lower:
                emoji = "🌫️"  # туман

            # делаем красивое сообщение с погодой
            weather_text = (
                f"🌍 **Город:** {city}\n"
                f"{emoji} **Погода:** {description.capitalize()}\n"
                f"🌡️ **Температура:** {temp}°C (ощущается как {feels_like}°C)\n"
                f"💧 **Влажность:** {humidity}%\n"
                f"💨 **Ветер:** {wind} м/с"
            )
            return weather_text
        else:
            return "Ошибка получения данных"  # если что-то пошло не так с апи
            
    except Exception as e:  # ловим все возможные ошибки
        return f"Ошибка получения данных {e}"

# обработчики сообщений от пользователя

# команда /start
@bot.message_handler(commands=['start'])
def send_about(message):
    # приветственный текст
    text = (
        "Я бот для выявления погоды\n\n"
        "**Автор:** Тигран Геворкян\n"
        "Нажми на кнопку ниже, чтобы начать"
    )
    # отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, text, reply_markup=get_keyboard(), parse_mode='Markdown')

# обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def send_welcome(message):
    if message.text == "О проекте":  # если нажали кнопку "О проекте"
        info_text = (
            "**Информация о проекте**\n\n"
            "Этот бот создан в учебных целях (УчиДома)"
        )
        bot.send_message(message.chat.id, info_text, parse_mode='Markdown')
        
    elif message.text == "Моя геопозиция":  # если нажали кнопку с гео
        # просим нажать на скрепку для отправки локации
        bot.send_message(
            message.chat.id, 
            "Нажмите на значок скрепки ниже",
            reply_markup=types.ReplyKeyboardRemove()  # убираем клавиатуру на время
        )
        bot.send_message(message.chat.id, "Жду вашу геопозицию", reply_markup=get_keyboard())

# обработка полученной геолокации
@bot.message_handler(content_types=['location'])
def send_weather(message):
    # получаем координаты из сообщения
    lat = message.location.latitude
    lon = message.location.longitude
    
    # говорим, что нужно подождать
    bot.send_message(message.chat.id, "Секунду")
    
    # получаем погоду по координатам
    weather_result = get_weather(lat, lon)
    
    # отправляем результат пользователю
    bot.send_message(message.chat.id, weather_result, parse_mode='Markdown')

# запуск бота
if __name__ == '__main__':
    print("бот запущен")
    bot.polling(none_stop=True)