import telebot
from telebot.types import ReplyKeyboardMarkup
import os

TOKEN = "8292056523:AAGY_0lfU8TvwWQq9l-EP2UDiaI_l9kp3fQ"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6727914616  
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Проверка пути к фото
photo_path = os.path.join(BASE_DIR, "img", "airpods-1.jpg")
print(f"Пытаюсь открыть файл по пути: {photo_path}")
print(f"Файл существует: {os.path.exists(photo_path)}")

# Словарь с товарами
products = {
    "Наушники Hoko": {
        "price": 500,
        "description": "🎧 Беспроводные наушники с чистым звуком HOKO, Нет в наличии!",
    },
    "Наушники AirPods 3": {
        "price": 700,
        "description": "AirPods 3 реплика с хорошим, чистым звуком",
        "photo": photo_path  # Используем уже проверенный путь
    }
}

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🛍️ Товары')
    markup.row('📱 Соцсети', '🆘 Поддержка')
    markup.row('⭐ Оставить отзыв')  
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в LitCombany!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == '🛍️ Товары')
def show_products(message):
    for name, data in products.items():
        try:
            if 'photo' in data and data['photo'] and os.path.exists(data['photo']):
                with open(data['photo'], 'rb') as photo_file:
                    bot.send_photo(
                        chat_id=message.chat.id,
                        photo=photo_file,
                        caption=f"🎧 {name}\n💰 Цена: {data['price']}₽\n📝 {data['description']}",
                        reply_markup=products_menu()
                    )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"🎧 {name}\n💰 Цена: {data['price']}₽\n📝 {data['description']}",
                    reply_markup=products_menu()
                )
        except Exception as e:
            print(f"Ошибка при отправке товара {name}: {str(e)}")
            bot.send_message(
                chat_id=message.chat.id,
                text=f"🎧 {name}\n💰 Цена: {data['price']}₽\n📝 {data['description']}\n\n⚠️ Фото временно недоступно",
                reply_markup=products_menu()
            )

def products_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Наушники Hoko', 'Наушники AirPods 3')
    markup.row('🔙 Назад')
    return markup
# Новый обработчик для отзывов
@bot.message_handler(func=lambda m: m.text == '⭐ Оставить отзыв')
def ask_review(message):
    msg = bot.send_message(message.chat.id, "Напишите ваш отзыв о нашем магазине:")
    bot.register_next_step_handler(msg, save_review)

def save_review(message):
    # Сохраняем в файл
    with open('reviews.txt', 'a', encoding='utf-8') as f:
        f.write(f"Отзыв от @{message.from_user.username}:\n{message.text}\n\n")
    

    bot.send_message(
        ADMIN_ID,
        f"📝 Новый отзыв!\nОт: @{message.from_user.username}\nТекст:\n{message.text}"
    )
    

    bot.send_message(
        message.chat.id,
        "Спасибо за ваш отзыв! 💙",
        reply_markup=main_menu()
    )

# Меню товаров
def products_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Наушники Hoko', 'Наушники AirPods 3')
    markup.row('🔙 Назад')
    return markup

# Обработчик /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в LitCombany! Выберите раздел:",
        reply_markup=main_menu()
    )

# Обработчик кнопки "Товары" (с фото)
@bot.message_handler(func=lambda m: m.text == '🛍️ Товары')
def show_products(message):
    try:

        for name, data in products.items():
            bot.send_photo(
                message.chat.id,
                data['photo'],
                caption=f"{name}\nЦена: {data['price']}₽\n{data['description']}"
            )
        bot.send_message(message.chat.id, "Выберите товар:", reply_markup=products_menu())
    except Exception as e:
        print(f"Ошибка при отправке фото: {e}")

        products_text = "\n\n".join(
            [f"{name} - {data['price']}₽\n{data['description']}" 
             for name, data in products.items()]
        )
        bot.send_message(message.chat.id, products_text, reply_markup=products_menu())

# Обработчик кнопки "Соцсети"
@bot.message_handler(func=lambda m: m.text == '📱 Соцсети')
def show_socials(message):
    bot.send_message(
        message.chat.id,
        "Наши соцсети:\n\n"
        "VK: vk.com/litcomb\n"
        "Instagram: @litcombany\n"
        "Telegram: @litComb",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda m: m.text == '🆘 Поддержка')
def show_support(message):
    bot.send_message(
        message.chat.id,
        "По вопросам пишите @greteiks",
        reply_markup=main_menu()
    )

orders = {}  

@bot.message_handler(func=lambda m: m.text in products.keys())
def select_product(message):
    product = message.text
    price = products[product]["price"]
    orders[message.chat.id] = {"product": product, "price": price}
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('✅ Подтвердить заказ', '❌ Отменить')
    
    bot.send_message(
        message.chat.id,
        f"Вы выбрали: *{product}*\nЦена: *{price}₽*\n\nПодтвердите заказ:",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: m.text == '✅ Подтвердить заказ')
def confirm_order(message):
    if message.chat.id not in orders:
        bot.send_message(message.chat.id, "❌ Ошибка: товар не выбран", reply_markup=main_menu())
        return
    
    order = orders[message.chat.id]
    user = message.from_user
    


    admin_msg = (
        f"🚀 *Новый заказ!*\n\n"
        f"▪ Товар: {order['product']}\n"
        f"▪ Цена: {order['price']}₽\n"
        f"▪ Клиент: @{user.username}\n"
        f"▪ ID: {user.id}\n"
        f"▪ Имя: {user.first_name} {user.last_name or ''}"
    )
    

    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    

    bot.send_message(
        message.chat.id,
        f"✅ Заказ принят! Товар: {order['product']}\n"
        f"Цена: {order['price']}₽\n"
        f"Мы свяжемся с вами в течение 30 минут.",
        reply_markup=main_menu()
    )
    

    del orders[message.chat.id]


@bot.message_handler(func=lambda m: m.text == '❌ Отменить')
def cancel_order(message):
    if message.chat.id in orders:
        del orders[message.chat.id]
    bot.send_message(
        message.chat.id,
        "❌ Заказ отменён",
        reply_markup=products_menu()
    )


@bot.message_handler(func=lambda m: m.text == '🔙 Назад')
def back_to_main(message):
    bot.send_message(
        message.chat.id,
        "Вы вернулись в главное меню",
        reply_markup=main_menu()
    )


faq = {
    "Доставка": "🚚 Отправляем в день заказа! Сроки: 3-5 дней по россии.",
    "Оплата": "💳 перевод на карту.",
    "Гарантия": "🔧 Возврат в течение 1 дня если товар не понравился."
}


@bot.message_handler(commands=['faq'])
def show_faq(message):
    text = "\n\n".join([f"**{q}**\n{a}" for q, a in faq.items()])
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

print("Бот запущен!")
bot.polling()