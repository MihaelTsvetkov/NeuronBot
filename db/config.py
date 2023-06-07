from db.database import Database1


class Config:
    def __init__(self, db: Database1):
        self.db = db

    def get_telegram_id(self):
        return self.db.get_telegram_id()

    def add_user_config(self, telegram_id, user_nickname, last_question, last_answer):
        return self.db.add_user_config(telegram_id, user_nickname, last_question, last_answer)

    def get_user_config(self, telegram_id):
        return self.db.get_user_config(telegram_id)
