 #!/usr/bin/env python3.9

# a background script that tracks queries to GPT and retrieves its responses
import os
import openai
import os

class ChatApp:
    def __init__(self):
        # Setting the API key to use the OpenAI API
        openai.api_key = "AAAAAAAAAAAAAAA"  # os.getenv("OPENAI_API_KEY")
        self.messages = [
            {"role": "system", "content": "You are an assistant for an elderly person."},
        ]


    # return the response
    def sendResponse(self, response):
        with open("gpt.txt", "w") as file:
            file.write(str(response))


    # retrieve the query
    def getQuery(self):
        output = ""
        if os.path.exists("askGPT.txt"):
            with open("askGPT.txt", "r") as f:
                output = f.read()
        return output


    # reset the query
    def resetQuestion(self):
        if os.path.exists("askGPT.txt"):
            os.remove("askGPT.txt")


    # retrieve the response
    def chat(self, message): #   , message
        self.messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        self.messages.append({"role": "assistant", "content": response["choices"][0]["message"].content})
        return response["choices"][0]["message"].content


if __name__ == "__main__":
    chatApp = ChatApp()
    while True:
        inp = chatApp.getQuery() #input("Please enter a msg: ")
        if inp == '':
            continue

        chatApp.resetQuestion() #delete file with question
        response = chatApp.chat(inp)
        print("response: ", response)
        chatApp.sendResponse(response)
