import openai


class ChatGpt:

    API_KEY = ""
    openai.api_key = API_KEY

    def chat_gpt_request(self, value):
        respone = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", "content": value
            }]
        )
        return respone["choices"][0]["message"]["content"]

    def transcribe(self, audio):
        return openai.Audio.transcribe("whisper-1", audio).get('text')


