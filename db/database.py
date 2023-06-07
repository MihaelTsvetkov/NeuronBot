import psycopg2
from db.convert import convert_list_for_int_and_float
import logging
from options import settings

logger = logging.getLogger(__name__)


class Database1:
    def __init__(self, host, port, user, password, dbname):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.prepare_database()

    def _get_connection(self):
        return psycopg2.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                database=self.dbname)

    def _get_connection_no_database(self):
        return psycopg2.connect(host=self.host, port=self.port, user=self.user, password=self.password)

    def get_telegram_id(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = "SELECT telegram_id FROM user_data"
                cursor.execute(query)
                result = cursor.fetchall()
            clear_result = convert_list_for_int_and_float(result)
            return clear_result

    def create_database(self):
        connection = None
        try:
            connection = self._get_connection_no_database()
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'neurobot'")
                exists = cursor.fetchone()
                if not exists:
                    logger.info("Creating db 'NeuroBot'")
                    cursor.execute('CREATE DATABASE neurobot')
        finally:
            connection.close()

    def prepare_database(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = """CREATE TABLE IF NOT EXISTS user_data (
                  telegram_id INTEGER,
                  user_nickname VARCHAR(256),
                  last_question VARCHAR(4096),
                  last_answer VARCHAR(4096),
                  count INTEGER
                  ) """
                cursor.execute(query)
                connection.commit()

    def add_user_config(self, telegram_id, user_nickname, last_question, last_answer):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = "SELECT last_question, last_answer, count from user_data WHERE telegram_id = %s"
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    query = "SELECT MAX (count) from user_data WHERE telegram_id = %s"
                    val = (telegram_id, )
                    cursor.execute(query, val)
                    result = cursor.fetchone()
                    max_v = result[0]
                    if max_v >= settings.NUMBER_OF_QUESTIONS_AND_ANSWERS_STORED:
                        max_v += 1
                        to_delete = max_v - (settings.NUMBER_OF_QUESTIONS_AND_ANSWERS_STORED - 1)
                        query = "DELETE FROM user_data WHERE telegram_id = %s and count = %s "
                        val = (telegram_id, to_delete)
                        cursor.execute(query, val)
                        query = "INSERT INTO user_data (telegram_id,  user_nickname, last_question, last_answer, " \
                                "count) values(%s, %s, %s, %s, %s)"
                        val = (telegram_id, user_nickname, last_question, last_answer, max_v)
                        cursor.execute(query, val)
                    else:
                        max_v += 1
                        query = "INSERT INTO user_data (telegram_id,  user_nickname, last_question, last_answer, " \
                                "count) values(%s, %s, %s, %s, %s)"
                        val = (telegram_id, user_nickname, last_question, last_answer, max_v)
                        cursor.execute(query, val)
                else:
                    query = "INSERT INTO user_data (telegram_id,  user_nickname, last_question, last_answer, count) " \
                            "values(%s, %s, %s, %s, %s)"
                    val = (telegram_id, user_nickname, last_question, last_answer, 1)
                    cursor.execute(query, val)
        connection.commit()

    def count_messages(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT COUNT (last_answer) FROM user_data WHERE telegram_id = %s"
                val = (telegram_id, )
                cursor.execute(sql, val)
                result = cursor.fetchone()
            return True if result[0] < settings.NUMBER_OF_QUESTIONS_AND_ANSWERS_STORED else False

    def get_user_config(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = "SELECT last_question, last_answer from user_data WHERE telegram_id = %s"
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchall()
            return result if result else False
