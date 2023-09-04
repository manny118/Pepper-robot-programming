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











"""
output = ""
if os.path.exists("askGPT.txt"):
    with open("askGPT.txt", "r") as f:
        output = f.read()
    #os.remove("askGPT.txt")
# userSpeech = "in few words: " + output
# print(userSpeech)
userSpeech = output
print("userSpeech here: ", userSpeech)

# {"role": "system", "content": "You are an assistant for an elderly person ."}
import json

prevConvo = []
if os.path.exists("trackConvo.json"):
    with open("trackConvo.json", "r") as f:
        #prevConvo = f.read()
        prevConvo = (json.load(f))
        #prevConvo = list(prevConvo.values())
"""

#print("userSpeech: ", userSpeech)

"""
print("prevConvo 1: ", (prevConvo))
#userSpeech = prevConvo + {"role": "user", "content": userSpeech} ## JSON
new_data = {"role": "user", "content": userSpeech}
prevConvo.append(new_data)
print("prevConvo 2: ", prevConvo)
"""


"""

with open("trackConvo.json", "w") as file:
    store_info = {"role": "assistant", "content": userSpeech}
    # file.write(str(store_info))
    json.dump(store_info, file, indent=4)


openai.api_key = "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"  #os.getenv("OPEN_API_KEY") #personal email
completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    max_tokens = 50,
    messages = prevConvo
    #messages = [
    #    {"role": "user", "content": userSpeech}
    #]
)


GPT_response = completion.choices[0].message.content

print("response:", GPT_response)


with open("gpt.txt", "w") as file:
    file.write(GPT_response)



with open("trackConvo.json", "w") as file:
    store_info = {"role": "assistant", "content": GPT_response}
    # file.write(str(store_info))
    json.dump(store_info, file, indent=4)
"""



"""
class ChatApp:
    def __init__(self):
        # Setting the API key to use the OpenAI API
        openai.api_key = "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"  # os.getenv("OPENAI_API_KEY")
        self.messages = [
            {"role": "system", "content": "You are an assistant for an elderly person."},
        ]


    def readText(self):
        output = ""
        if os.path.exists("askGPT.txt"):
            with open("askGPT.txt", "r") as f:
                output = f.read()
        return output

    def chat(self, message): #   , message
        #message = self.readText()
        self.messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        self.messages.append({"role": "assistant", "content": response["choices"][0]["message"].content})
        return response["choices"][0]["message"]

if __name__ == "__main__":
    chatApp = ChatApp()
    chatApp.chat()
"""

        # return response["choices"][0]["message"]



#"""
#serial
#  4+gxzkD6xlRxh9bjjZYO+aPhqrG2p1IiQvbnEDgBEw4=
#
