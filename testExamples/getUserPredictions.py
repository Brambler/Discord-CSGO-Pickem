import requests
import json

# with open('data.json') as f:
#     data = json.load(f)
#     steam_api_key = data['steam_api_key']
#     users_steamid = data['users_steamid']
#     user_auth_code = data['users_auth_code']
#     event = data['event_id']

def getPickemInfo(api_key, event, steamID, authCode):
    getTournamentLayout_url = f"https://api.steampowered.com/ICSGOTournaments_730/GetTournamentLayout/v1?key={steam_api_key}&event={event}"
    tournamentLayoutResponse = requests.get(getTournamentLayout_url)

    tournamentVar_json = json.loads(tournamentLayoutResponse.text)
    tournamentVar_name = tournamentVar_json['result']['name']

    # Access the picks for different stages
    tournamentVar_preliminary_stage_picks = tournamentVar_json["result"]["sections"][0]["groups"]
    tournamentVar_quarterfinals_picks = tournamentVar_json["result"]["sections"][2]["groups"]
    tournamentVar_semifinals_picks = tournamentVar_json["result"]["sections"][3]["groups"]
    tournamentVar_grand_final_picks = tournamentVar_json["result"]["sections"][4]["groups"]

    # Load team information from the first JSON response
    teams_info = tournamentVar_json["result"]["teams"]

    # Define a function to get the team name by pickid
    def get_team_name_by_pickid(pickid, teams):
        for team in teams:
            if team["pickid"] == pickid:
                return team["name"]
        return None

    # Get user Predictions
    getPredictions_url = f"https://api.steampowered.com/ICSGOTournaments_730/GetTournamentPredictions/v1?key={api_key}&event={event}&steamid={steamID}&steamidkey={authCode}"

    predictions_response = requests.get(getPredictions_url)
    predictions_response_json = json.loads(predictions_response.text)

    # Access the picks from the JSON data
    current_picks = predictions_response_json["result"]["picks"]

    # Print the current picks with team names
    print("Current Picks:")

    # Print 3-0 and 0-3 picks first
    for pick in current_picks:
        team_name = get_team_name_by_pickid(pick['pick'], teams_info)
        if pick['index'] == 0:
            print(f"3-0 Pick:        {team_name}")
        elif pick['index'] == 8:
            print(f"0-3 Pick:        {team_name}")

    # Print the rest of the picks
    for pick in current_picks:
        team_name = get_team_name_by_pickid(pick['pick'], teams_info)
        if 1 <= pick['index'] <= 7:
            print(f"To Advance Pick: {team_name}")