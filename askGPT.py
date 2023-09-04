#!/usr/bin/env python3.9

# a script for querying GPT-3.5
import os
import openai
import os


userSpeech = ""
if os.path.exists("askGPT.txt"):
    with open("askGPT.txt", "r") as f:
        userSpeech = f.read()

userSpeech = output
print("userSpeech: ", userSpeech)

# query GPT
openai.api_key = "AAAAAAAAAAAAAAA"# os.getenv("OPEN_API_KEY")
completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    max_tokens = 50,
    messages = [
        {"role": "user", "content": userSpeech}
    ]
)

# retrieve the response
GPT_response = completion.choices[0].message.content
print("response:", GPT_response)
with open("gpt.txt", "w") as file:
    file.write(GPT_response)
