import os
import telebot
from dotenv import dotenv_values
from google_images_search import GoogleImagesSearch
import openai

from telebot import types

config = dotenv_values('.env')
token = config['BOT_TOKEN']
gpt_api_key = config['GPT_API_KEY']
google_api_key = config['GOOGLE_API_KEY']
google_cse_id = config['GOOGLE_CSE_ID']
bot = telebot.TeleBot(token)

openai.api_key = gpt_api_key
gis = GoogleImagesSearch(google_api_key, google_cse_id)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()

    # Tạo các nút tương tác cho menu
    btn1 = types.InlineKeyboardButton('Lựa chọn 1', callback_data='option1')
    btn2 = types.InlineKeyboardButton('Lựa chọn 2', callback_data='option2')
    btn3 = types.InlineKeyboardButton('Lựa chọn 3', callback_data='option3')

    # Thêm các nút vào menu
    markup.add(btn1, btn2, btn3)

    # Gửi menu đến người dùng
    bot.send_message(message.chat.id, 'Chọn một lựa chọn:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'option1':
        # Xử lý lựa chọn 1
        bot.send_message(call.message.chat.id, 'Bạn đã chọn lựa chọn 1.')
    elif call.data == 'option2':
        # Xử lý lựa chọn 2
        bot.send_message(call.message.chat.id, 'Bạn đã chọn lựa chọn 2.')
    elif call.data == 'option3':
        # Xử lý lựa chọn 3
        bot.send_message(call.message.chat.id, 'Bạn đã chọn lựa chọn 3.')

def complete_prompt(prompt):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": f"I am Chí Năng Sóp Pi, a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


@bot.message_handler(commands=['img'])
def handle_image_search(message):
    query = message.text[5:].strip()

    search_params = {
        'q': query,
        'num': 5,  # Number of images to retrieve (adjust as needed)
        'safe': 'medium',
        'fileType': 'jpg|png',  # Limit the file types to JPG and PNG
        'imgSize': 'medium',
        'imgType': 'photo'
    }

    # Perform image search
    gis.search(search_params)
    images = gis.results()

    if images:
        image_url = images[0].url
        bot.send_photo(message.chat.id, image_url)
    else:
        bot.reply_to(message, "No images found.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    prompt = message.text
    response = complete_prompt(prompt)


    try:
        if '```' in response:
            formatted_response = response.strip('`')
            if message.reply_to_message:
                if message.chat.type == 'private':
                    bot.reply_to(
                        message.reply_to_message, formatted_response, parse_mode='Markdown')
                else:
                    bot.reply_to(
                        message.reply_to_message, formatted_response)
            else:
                if message.chat.type == 'private':
                    bot.send_message(
                        message.chat.id, formatted_response, parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, formatted_response)
        else:
            if message.reply_to_message:
                if message.chat.type == 'private':
                    bot.reply_to(message.reply_to_message, response)
                else:
                    bot.reply_to(message.reply_to_message, response)
            else:
                if message.chat.type == 'private':
                    bot.send_message(message.chat.id, response)
                else:
                    bot.send_message(message.chat.id, response)
    except telebot.apihelper.ApiTelegramException as e:
        bot.send_message(
            message.chat.id, "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.")
        print(f"Telegram API Error: {e}")


def search_images(query):
    gis.search({'q': query, 'num': 5})  # Search for 5 images
    results = gis.results()

    image_urls = []
    for result in results:
        image_urls.append(result.url)

    return image_urls


# Start the bot
bot.infinity_polling()
