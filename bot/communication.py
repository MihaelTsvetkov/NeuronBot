from pydub import AudioSegment
from telebot import types
from open_ai.chatgpt import chat_gpt_response
from open_ai.transcribe import transcribe
from open_ai.dalle import dall_e_response
from localization.json_translate import get_json_localization
from options import settings
import os
import logging
import openai.error
import datetime

logger = logging.getLogger(__name__)


class Communication:
    def __init__(self, cnf, bot, process_message):
        self.gpt_response = None
        self.state = None
        self.dall_e_response = None
        self.cnf = cnf
        self.bot = bot
        self.process_message = process_message

    def get_telegram_id(self):
        return self.cnf.get_telegram_id()

    def run(self, message):
        self.state(message)

    def state_greetings(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(get_json_localization("chat_gpt_btn"))
        markup.add(get_json_localization("dall_e_btn"))
        self.bot.send_message(message.chat.id, get_json_localization("greetings"), reply_markup=markup)
        self.state = self.state_choose

    def state_choose(self, message):
        user_message = message.text.strip()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(get_json_localization("back_btn"))

        if user_message == get_json_localization("chat_gpt_btn"):
            self.state = self.gpt_request

        elif user_message == get_json_localization("dall_e_btn"):
            self.state = self.dall_e_request

        self.bot.send_message(message.chat.id, get_json_localization("enter_a_query"), reply_markup=markup)

    def gpt_request(self, message):
        if bool(message.text):
            message_from_user = message.text.strip()
            if message_from_user == get_json_localization("back_btn"):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(get_json_localization("chat_gpt_btn"))
                markup.add(get_json_localization("dall_e_btn"))
                self.state = self.state_choose
                self.bot.send_message(message.chat.id, get_json_localization("menu"), reply_markup=markup)
                return

        if not bool(message.text):
            user_message = str(transcribe(self.prepare_audio(message)))
            os.remove(settings.OGG_FILE_PATH)
            os.remove(settings.MP3_FILE_PATH)
        else:
            user_message = message.text.strip()
        logger.info(f'{get_json_localization("request_to_chat_gpt")}: {message.from_user.username}, '
                    f'{get_json_localization("request")} {user_message}, '
                    f'{get_json_localization("time")} '
                    f"{datetime.datetime.now()}")
        self.state = None
        self.bot.send_message(message.chat.id, get_json_localization("request_has_been_sent"))
        try:
            previous_questions_and_answers = self.cnf.get_user_config(message.chat.id)
            self.gpt_response = chat_gpt_response(previous_questions_and_answers=previous_questions_and_answers,
                                                  new_question=str(user_message))

        except openai.error.RateLimitError:
            self.bot.send_message(message.chat.id, get_json_localization("requests exceeded"))
        self.bot.send_message(message.chat.id, self.gpt_response)
        tuple_of_question = (user_message,)
        tuple_of_answer = (self.gpt_response,)
        self.cnf.add_user_config(message.chat.id, message.from_user.username, tuple_of_question, tuple_of_answer)
        self.gpt_response = None
        self.state = self.gpt_request
        self.bot.send_message(message.chat.id, get_json_localization("enter_a_query"))

    def dall_e_request(self, message):
        if bool(message.text):
            message_from_user = message.text.strip()
            if message_from_user == get_json_localization("back_btn"):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add(get_json_localization("chat_gpt_btn"))
                markup.add(get_json_localization("dall_e_btn"))
                self.state = self.state_choose
                self.bot.send_message(message.chat.id, get_json_localization("menu"), reply_markup=markup)
                return

        if not bool(message.text):
            self.state = None
            user_message = str(transcribe(self.prepare_audio(message)))
            os.remove(settings.OGG_FILE_PATH)
            os.remove(settings.MP3_FILE_PATH)
        else:
            user_message = message.text.strip()
        logger.info(f'{get_json_localization("request_to_dall-e")}: {message.from_user.username}, '
                    f'{get_json_localization("request")} {user_message}, '
                    f'{get_json_localization("time")} '
                    f"{datetime.datetime.now()}")
        self.state = None
        self.bot.send_message(message.chat.id, get_json_localization("request_has_been_sent"))
        try:
            self.dall_e_response = dall_e_response(str(user_message))
        except openai.error.RateLimitError:
            self.bot.send_message(message.chat.id, get_json_localization("requests_exceeded"))
        self.bot.send_message(message.chat.id, self.dall_e_response)
        self.dall_e_response = None
        self.state = self.dall_e_request
        self.bot.send_message(message.chat.id, get_json_localization("enter_a_query"))

    def prepare_audio(self, message):
        file_info = self.bot.get_file(message.voice.file_id)
        downloaded_file = self.bot.download_file(file_info.file_path)

        with open('new_file.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
        sound = AudioSegment.from_file(settings.OGG_FILE_PATH)
        return sound.export(settings.MP3_FILE_PATH, format="mp3")

    def is_finished(self):
        return self.state is None
