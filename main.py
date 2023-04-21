import os
import threading
import openai.error
import telebot
from pydub import AudioSegment
from telebot import types
from chatgpt import ChatGpt


token = ""
chatgpt3_but = "ChatGpt3"


class FSM:
    def __init__(self):
        self.state = None
        self.bot = telebot.TeleBot(token, threaded=True)
        self.response = None
        self.lock = threading.RLock()
        self.answer = False

        @self.bot.message_handler(commands=['start'])
        def launch(message):
            with self.lock:
                self.start_command(message)

        @self.bot.message_handler(content_types=['text', 'voice'])
        def call_process_message(message):
            self.process_message(message)

    def run_fsm(self, message):
        if self.state is not None:
            self.run(message)

    def start_command(self, message):
        self.start(message)

    def process_message(self, message):
        if self.state is not None:
            self.run_fsm(message)

    def run(self, message):
        self.state(message)

    def is_finished(self):
        return self.state is None

    def start(self, message):
        self.state = self.state_greetings
        self.run(message)

    def state_greetings(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        markup.add(chatgpt3_but)
        self.bot.send_message(message.chat.id, 'Приветствую ! Я бот GPT, помогу вам в общении с нейросетью от openai. '
                                               '\nДля продолжения просто нажмите кнопку '
                                               '"ChatGpt3" и введите свой запрос\n'
                                               '(Вcе вырученные деньги пойдут на покупку автомобиля Audi A4 для'
                                               ' моего разработчика)', reply_markup=markup)
        self.state = self.state_choose

    def state_choose(self, message):
        user_message = message.text.strip()

        if user_message == "ChatGpt3":
            self.state = self.gpt_request
            self.bot.send_message(message.chat.id, "Введите запрос", reply_markup=types.ReplyKeyboardRemove())

    def gpt_request(self, message):
        gpt = ChatGpt()
        if not bool(message.text):
            user_message = str(gpt.transcribe(self.prepare_audio(message)))
            os.remove("Your path to audio file")
            os.remove("Your path to audio file")
        else:
            user_message = message.text.strip()
        print(f"Запрос к chatgpt от пользователя: {message.from_user.username}, запрос: {user_message}")
        self.state = None
        self.bot.send_message(message.chat.id, 'Запрос отправлен, ожидайте')
        try:
            self.response = gpt.chat_gpt_request(str(user_message))
        except openai.error.RateLimitError:
            self.bot.send_message(message.chat.id, 'Похоже вы превысили лимит по запросам к нейросети '
                                                   'в минуту! Но ничего страшного,'
                                                   ' совсем скоро вы сможете заплатить за совршенную gpt-4, '
                                                   'которая не имеет лимитов! (Все вырученные средства пойдут '
                                                   'на покупку Audi A4 для разработчика !)')
        self.bot.send_message(message.chat.id, self.response)
        self.response = None
        self.state = self.gpt_request
        self.bot.send_message(message.chat.id, "Введите запрос", )

    def prepare_audio(self, message):
        file_info = self.bot.get_file(message.voice.file_id)
        downloaded_file = self.bot.download_file(file_info.file_path)

        with open('new_file.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
        sound = AudioSegment.from_file("Your path to audio file")
        return sound.export("Your path to audio file")

    def polling(self):
        self.bot.infinity_polling()


if __name__ == "__main__":
    bt = FSM()
    bt.polling()
