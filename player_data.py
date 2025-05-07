import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

print("Player details:\n**************")

api_key = os.getenv("API_KEY")
name = input("Digite seu nickname: ")
tag = input("Digite sua tag (sem a #): ")
headers = {
    "Authorization": f"{api_key}"
  }

url = f'https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}'
response = requests.get(url, headers=headers)
data = response.json()

with open('player_data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)
    
print("Dados salvos no arquivo 'player_data.json'!")