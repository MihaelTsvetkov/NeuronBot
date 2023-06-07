import openai
from options import settings

openai.api_key = settings.API_TOKEN


def chat_gpt_response(previous_questions_and_answers=None, new_question=None):
    messages = []
    if previous_questions_and_answers:

        for question, answer in previous_questions_and_answers:
            messages.append({"role": "user", "content": question})
            messages.append({"role": "user", "content": answer})

    messages.append({"role": "user", "content": new_question})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response["choices"][0]["message"]["content"]
