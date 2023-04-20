import openai


class ChatGpt:
    def __init__(self, value):
        self.value = value

    API_KEY = "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"
    openai.api_key = API_KEY

    def chat_gpt_request(self):
        respone = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", "content": self.value
            }]
        )
        return respone["choices"][0]["message"]["content"]


