import telebot
from telebot.types import ReplyKeyboardMarkup, InputMediaPhoto

TOKEN = "8292056523:AAGY_0lfU8TvwWQq9l-EP2UDiaI_l9kp3fQ"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6727914616  # Ваш ID в Telegram

# Словарь с товарами, ценами и фото
products = {
    "Наушники": {
        "price": 500,
        "description": "🎧 Беспроводные наушники с чистым звуком",
        "photo": "https://cdn1.ozone.ru/s3/multimedia-3/6049421991.jpg"
    },
    "PowerBank": {
        "price": 800,
        "description": "🔋 Мощный powerbank 10000 mAh",
        "photo": "https://cache3.youla.io/files/images/780_780/58/3a/583a9273080cbddf36f63482.jpg"
    }
}

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🛍️ Товары')
    markup.row('📱 Соцсети', '🆘 Поддержка')
    markup.row('⭐ Оставить отзыв')  # Новая кнопка
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
    
    # Отправляем админу
    bot.send_message(
        ADMIN_ID,
        f"📝 Новый отзыв!\nОт: @{message.from_user.username}\nТекст:\n{message.text}"
    )
    
    # Подтверждаем пользователю
    bot.send_message(
        message.chat.id,
        "Спасибо за ваш отзыв! 💙",
        reply_markup=main_menu()
    )

# Меню товаров
def products_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Наушники', 'PowerBank')
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
        # Отправляем каждое фото отдельным сообщением с описанием
        for name, data in products.items():
            bot.send_photo(
                message.chat.id,
                data['photo'],
                caption=f"{name}\nЦена: {data['price']}₽\n{data['description']}"
            )
        bot.send_message(message.chat.id, "Выберите товар:", reply_markup=products_menu())
    except Exception as e:
        print(f"Ошибка при отправке фото: {e}")
        # Если фото не отправилось - текстовый вариант
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

# Обработчик кнопки "Поддержка"
@bot.message_handler(func=lambda m: m.text == '🆘 Поддержка')
def show_support(message):
    bot.send_message(
        message.chat.id,
        "По вопросам пишите @greteiks",
        reply_markup=main_menu()
    )

orders = {}  # Временное хранилище заказов

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

# Обработчик подтверждения заказа
@bot.message_handler(func=lambda m: m.text == '✅ Подтвердить заказ')
def confirm_order(message):
    if message.chat.id not in orders:
        bot.send_message(message.chat.id, "❌ Ошибка: товар не выбран", reply_markup=main_menu())
        return
    
    order = orders[message.chat.id]
    user = message.from_user
    
    # Формируем сообщение для админа
    admin_msg = (
        f"🚀 *Новый заказ!*\n\n"
        f"▪ Товар: {order['product']}\n"
        f"▪ Цена: {order['price']}₽\n"
        f"▪ Клиент: @{user.username}\n"
        f"▪ ID: {user.id}\n"
        f"▪ Имя: {user.first_name} {user.last_name or ''}"
    )
    
    # Отправляем админу
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    
    # Подтверждение пользователю
    bot.send_message(
        message.chat.id,
        f"✅ Заказ принят! Товар: {order['product']}\n"
        f"Цена: {order['price']}₽\n"
        f"Мы свяжемся с вами в течение 30 минут.",
        reply_markup=main_menu()
    )
    
    # Очищаем заказ
    del orders[message.chat.id]

# Обработчик отмены заказа
@bot.message_handler(func=lambda m: m.text == '❌ Отменить')
def cancel_order(message):
    if message.chat.id in orders:
        del orders[message.chat.id]
    bot.send_message(
        message.chat.id,
        "❌ Заказ отменён",
        reply_markup=products_menu()
    )

# Обработчик кнопки "Назад"
@bot.message_handler(func=lambda m: m.text == '🔙 Назад')
def back_to_main(message):
    bot.send_message(
        message.chat.id,
        "Вы вернулись в главное меню",
        reply_markup=main_menu()
    )

# FAQ
faq = {
    "Доставка": "🚚 Отправляем в день заказа! Сроки: 3-5 дней по россии.",
    "Оплата": "💳 перевод на карту.",
    "Гарантия": "🔧 Возврат в течение 3 дней если товар не понравился."
}

@bot.message_handler(commands=['faq'])
def show_faq(message):
    text = "\n\n".join([f"**{q}**\n{a}" for q, a in faq.items()])
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

print("Бот запущен!")
bot.polling()