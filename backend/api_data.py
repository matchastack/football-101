import requests
import os
from dotenv import load_dotenv
import pandas as pd
import pickle

load_dotenv()

HEADER = {
        "x-rapidapi-host" : os.getenv("RAPIDAPI_HOST"),
        "x-rapidapi-key" : os.getenv("RAPIDAPI_KEY")
    }

def store_pkl(fname, object):
    with open(fname, 'wb') as f:
        pickle.dump(object, f)
    return

def load_pkl(fname):
    with open(fname, 'rb') as f:
        return pickle.load(f)

def make_url(endpoint):
    return f"https://api-football-vl.p.rapidapi.com/v3{endpoint}"

def get_api_response(endpoint, headers=HEADER, method="GET"):
    url = make_url(endpoint)
    response = requests.request(method, url, headers=headers)
    return response

def get_leagues():
    df = pd.DataFrame()

    ## get leagues data from api
    r = get_api_response("/leagues")

    ## if response is successful, convert to pandas df
    if r.status_code == 200:
        ## unnest top layer json response, convert to pandas df
        df = pd.json_normalize(r.json()["response"])
        ## unnest seasons column (list of dicts)
        df = df.explode("seasons").reset_index(drop=True)
        ## unnest seasons column (dict)
        df = df.join(pd.json_normalize(df["seasons"])).drop(columns=["seasons"])

    return df