import pandas as pd
from api_data import get_api_response
import time

def fixtures_csv(league_id:int, season:int):
    df = pd.DataFrame()

    ## set args
    args = {"league" : league_id, "season": season}

    ## get fixtures data from api
    r = get_api_response("/fixtures", args=args)

    ## if response is successful, convert to pandas df
    if r.status_code == 200:
        ## unnest top layer json response, convert to pandas df
        df = pd.json_normalize(r.json()["response"])

    return df

if __name__ == "__main__":
    df = pd.DataFrame()
    
    seasons = [i for i in range(1992, 2023)]
    for season in seasons:
        df = pd.concat([df, fixtures_csv(league_id=39, season=season)])
        time.sleep(5)
        

    df.to_csv("../data/fixtures.csv", index=False)