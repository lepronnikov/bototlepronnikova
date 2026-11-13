import telebot
import requests
import phonenumbers
from phonenumbers import geocoder, carrier
import urllib.parse
from bs4 import BeautifulSoup
import re

BOT_TOKEN = "9142285213:AAEVs3g5z8ihrrhJk3EfzqpBL-gcyu0GluY"
bot = telebot.TeleBot(BOT_TOKEN)

def is_valid_email(email):
    # Регулярное выражение для проверки валидности почты
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "Привет! Отправь мне номер (+7...), почту или @ник.")

@bot.message_handler(func=lambda message: True)
def search_handler(message):
    query = message.text.strip()
    
    # ПРОВЕРКА НА НОМЕР
    if query.startswith("+") or query.isdigit():
        try:
            parsed = phonenumbers.parse(query, None)
            # Строгая проверка: существует ли такой номер вообще
            if not phonenumbers.is_possible_number(parsed) or not phonenumbers.is_valid_number(parsed):
                bot.send_message(message.chat.id, "❌ Ошибка: Такого номера не существует или он введен неверно. Проверьте формат (+7 XXX XXX-XX-XX).")
                return

            op = carrier.name_for_number(parsed, "ru")
            reg = geocoder.description_for_number(parsed, "ru")
            clean_num = query.replace("+", "").replace(" ", "").replace("-", "")
            
            result = "📱 Номер: " + query + "\n"
            result += "🌍 Регион: " + str(reg) + "\n"
            result += "📶 Оператор: " + str(op) + "\n\n"
            result += "🔍 Ссылки для проверки:\n"
            result += "VK: https://vk.com/search?c[q]=" + clean_num + "\n"
            result += "WhatsApp: https://wa.me/" + clean_num + "\n"
            result += "GetContact: https://getcontact.com/ru/search?q=" + clean_num + "\n"
            result += "Google: https://google.com/search?q=" + clean_num + "\n"
            result += "Avito: https://avito.ru/all?q=" + clean_num + "\n"
            
            bot.send_message(message.chat.id, result)
        except Exception as e:
            bot.send_message(message.chat.id, "❌ Ошибка при обработке номера. Убедитесь, что номер введен верно.")
            
    # ПРОВЕРКА НА ПОЧТУ
    elif "@" in query and "." in query:
        if not is_valid_email(query):
            bot.send_message(message.chat.id, "❌ Ошибка: Некорректный формат почты. Пример: test@mail.ru")
            return
            
        bot.send_message(message.chat.id, "🔄 Сканирую почту...")
        bot.send_message(message.chat.id, "📧 Проверь почту тут:\nhttps://haveibeenpwned.com/unifiedsearch/" + query + "\nhttps://leakcheck.io/result?query=" + query)
        
    # ПРОВЕРКА НА ЮЗЕРНЕЙМ
    elif query.startswith("@"):
        if len(query) < 4:
            bot.send_message(message.chat.id, "❌ Ошибка: Слишком короткий юзернейм.")
            return
            
        bot.send_message(message.chat.id, "🔄 Сканирую Telegram...")
        clean_user = query.replace('@', '')
        url = "https://t.me/" + clean_user
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.find('meta', property='og:title')
                desc = soup.find('meta', property='og:description')
                name = title['content'] if title else "Скрыто"
