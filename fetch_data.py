import requests
import dotenv
import os
import pathlib
import json
import time
import numpy as np

dotenv.load_dotenv()
USERNAME = os.getenv('GUSERNAME')
PASSWORD = os.getenv('GPASSWORD')

def get_auth_token():
    url = 'https://api.gplan.in/game/login'
    data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(url, json=data)
    if response.status_code != 200: raise Exception(response.text)
    return response.json()['accessToken']

class AUTHTOKEN:
    _token = None

    @classmethod
    def get(cls):
        if cls._token is None:
            cls._token = get_auth_token()
        return cls._token

def get_game_data(level):
    url = f"https://api.gplan.in/game/level/{level}"
    headers = {"Authorization": f"Bearer {AUTHTOKEN.get()}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200: raise Exception(response.text)
    data = response.json()
    data['graph'] = json.loads(data['graph'])
    return data

def get_game_image(level):
    url = f"https://api.gplan.in/game/static/image/levels/{level}.png"
    headers = {"Authorization": f"Bearer {AUTHTOKEN.get()}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200: raise Exception(response.text)
    return response.content

def download(level):
    directory = pathlib.Path(f"./data/{level}")
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / f"{level}.json"
    image_path = directory / f"{level}.png"

    if not json_path.exists():
        game_data = get_game_data(level)
        with open(json_path, "w") as json_file:
            json.dump(game_data, json_file, indent=4)

    if not image_path.exists():
        game_image = get_game_image(level)
        with open(image_path, "wb") as image_file:
            image_file.write(game_image)

def load_data(level):
    directory = pathlib.Path(f"./data/{level}")
    json_path = directory / f"{level}.json"

    if not json_path.exists():
        download(level)

    with open(json_path, "r") as json_file:
        return json.load(json_file)

def processed_data(lvl):
    data = load_data(lvl)
    grid_size = (data['grid']['row_size'],  data['grid']['column_size'])
    rotate = data['allowRotation']
    
    def remove_padding(arr):
        return arr[~np.all(arr == 0, axis=1)][:, ~np.all(arr == 0, axis=0)]
    tiles = {}
    for tile in data['graph']['nodes']:
        tiles[tile['id'] - 1] = remove_padding(np.array(tile['shape']))
    
    n = len(tiles)
    adj = np.zeros((n, n), dtype=bool)
    for i, j in data['graph']['edges']:
        adj[i, j] = True
        adj[j, i] = True
    return grid_size, tiles, adj, rotate

if __name__ == "__main__":
    LEVELS = 49
    for level in range(1, LEVELS+1):
        download(level)
        time.sleep(0.5)