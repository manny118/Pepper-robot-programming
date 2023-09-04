# Script for playing a user's favorite song

import requests
import time
import urllib.parse, urllib3.request
from bs4 import BeautifulSoup
import json
import os
import re
import subprocess


# clears the answer to the previous question answered by ChatGPT
def resetAnswer():
    if os.path.exists("gpt.txt"):
        open('gpt.txt', 'w').close()
resetAnswer()


# Queries ChatGPT for a response
def askGPT(response):
    with open("askGPT.txt", "w") as file:
        file.write(response)

    GPT_response = ""
    if os.path.exists("gpt.txt"):
        while True:
            with open("gpt.txt", "r") as file:
                GPT_response = file.read()
            if len(str(GPT_response)) < 2:
                continue
            else:
                resetAnswer()
                break
    return GPT_response

# ask ChatGPT first after extracting the info for fav music
# "in quotes, based on the above: what is my favorite song

with open("details.json", "r") as info:
    details = json.load(info)

favsong = details["favsong"]
print("favsong: ", favsong)

# to allow for variations
getTitle = favsong + ". Responding with the title and artist only in quotes, based on the above: what is my favorite song?"
print("question: ", getTitle)

GPT_response = askGPT(getTitle)
print("title: ", GPT_response)


music_name = GPT_response
query_string = urllib.parse.urlencode({"search_query": music_name})
formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)

search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
clip = requests.get("https://www.youtube.com/watch?v=" + "{}".format(search_results[0]))
clip2 = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])

print("clip2: ", clip2)

with open("music.txt", "w") as f:
    f.write(clip2)
