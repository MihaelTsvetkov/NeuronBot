import logging
import telebot
from db.config import Config
from db.database import Database1
from options import settings
from bot.communication import Communication
from options import log_settings
import threading

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.current_fsm_dict = dict()
        self.current_fsm_dict_lock = threading.RLock()
        self.bot = telebot.TeleBot(settings.BOT_TOKEN, threaded=True)
        self.db = Database1(host=settings.DATABASE_HOST, port=settings.DATABASE_PORT, user=settings.DATABASE_USER,
                            password=settings.DATABASE_PASSWD, dbname=settings.DATABASE)
        self.cnf = Config(self.db)

        @self.bot.message_handler(commands=['start'])
        def launch(message):
            self.start_fsm(message)

        @self.bot.message_handler(content_types=['text', 'voice'])
        def call_process_message(message):
            if self.current_fsm_dict is not None:
                self.process_message(message)

    def start_fsm(self, message):
        telegram_id = message.from_user.id
        with self.current_fsm_dict_lock:
            self.current_fsm_dict[telegram_id] = Communication(self.cnf, self.bot, self.process_message)
            self.current_fsm_dict[telegram_id].state_greetings(message)

    def run_fsm(self, message):
        telegram_id = message.from_user.id
        with self.current_fsm_dict_lock:
            if self.current_fsm_dict.get(telegram_id) is not None:
                self.current_fsm_dict[telegram_id].run(message)
                if self.current_fsm_dict[telegram_id].is_finished():
                    self.current_fsm_dict[telegram_id] = None

    def process_message(self, message):
        telegram_id = message.from_user.id
        with self.current_fsm_dict_lock:
            if self.current_fsm_dict.get(telegram_id) is not None:
                self.run_fsm(message)

    def polling(self):
        self.bot.infinity_polling()


def setup_logging(level):
    log_settings.setup_logging(level, settings.DEBUG_FILE_PATH, settings.INFO_FILE_PATH)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)


if __name__ == "__main__":
    bt = TelegramBot()
    setup_logging(settings.LOGGING_LEVEL)
    bt.polling()
