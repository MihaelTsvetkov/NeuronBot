import openai


def transcribe(audio):
    return openai.Audio.transcribe("whisper-1", audio).get('text')
