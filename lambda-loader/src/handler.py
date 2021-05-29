import api
import data
from predictions import Predictions
from dotenv import load_dotenv
import os

def add_leaderboards_to_db(database):
    tup = api.getLeaderboardSnapshot(verbose=False)
    snapshot = tup[0]
    lastUpdated = tup[1]

    for region in snapshot.keys():
        timeLast = database.get_time(region)
        timeCurrent = database.parse_time(lastUpdated[region])
        if timeCurrent >= timeLast: ## allow equal time for easy testing
            if (region == 'US'):
                handlePredictions(database, snapshot, 'lii', 'US')

            database.put_time(region, timeCurrent)
            database.put_items(region, snapshot[region])

def handlePredictions(database, snapshot, name, region):
    client_id = os.environ['CLIENT_ID']
    access_token = os.environ['ACCESS_TOKEN']

    predicter = Predictions(client_id, access_token)

    # Automatic prediction module
    lii_rating = database.get_item(region, name)['Ratings'][-1]
    
    # Rating gain
    if int(snapshot[region][name]['rating'] > lii_rating):
        predicter.run(True)
    # Rating loss
    if int(snapshot[region][name]['rating'] < lii_rating):
        predicter.run(False)

def handler(event, context):
    load_dotenv()
    
    database = data.RankingDatabaseClient()
    add_leaderboards_to_db(database)

