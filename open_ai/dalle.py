import openai


def dall_e_response(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response["data"][0]["url"]
