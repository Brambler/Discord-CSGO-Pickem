import requests
import json

steam_api_key = ""
users_steamid = ""
# Paris
user_auth_code = ""
event = "21"

# Rio
# user_auth_code = ""
# event = "20"

with open('testExamples/ChampionResponseExample.json', 'r') as file:
    fakeData = json.load(file)


def getChallengerPickemInfo(api_key, event, steamID, authCode):
    getTournamentLayout_url = f"https://api.steampowered.com/ICSGOTournaments_730/GetTournamentLayout/v1?key={steam_api_key}&event={event}"
    tournamentLayoutResponse = requests.get(getTournamentLayout_url)

    tournamentVar_json = json.loads(tournamentLayoutResponse.text)

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

    # predictions_response = requests.get(getPredictions_url)
    # predictions_response_json = json.loads(fakeData)
  

## Access the picks from the JSON data
    current_picks = fakeData["result"]["picks"]

    # print("Current Picks:")
    current_picks_sorted = sorted(current_picks, key=lambda x: x['groupid'])

    for groupid in [226, 227, 228, 229, 230, 231, 232]:
        for pick in current_picks_sorted:
            if pick['groupid'] == groupid:
                pick_index = pick['index']
                team_name = get_team_name_by_pickid(pick['pick'], teams_info)
                if pick_index == 0 and groupid == 226:
                    qmatch1pick = team_name
                elif pick_index == 0 and groupid == 227:
                    qmatch2pick = team_name
                elif pick_index == 0 and groupid == 228:
                    qmatch3pick = team_name
                elif pick_index == 0 and groupid == 229:
                    qmatch4pick = team_name
                elif pick_index == 0 and groupid == 230:
                    smatch1pick = team_name
                elif pick_index == 0 and groupid == 231:
                    smatch2pick = team_name
                elif pick_index == 0 and groupid == 232:
                    cmatchpick = team_name

    championsEmbed = discord.Embed(title="BLAST.tv Paris 2023 CS:GO Major Championship",description="Bramble's Current Legend's Pick'em",color=0xfffe0f)
    championsEmbed.add_field(name="Quarter Finals",value=f"{qmatch1pick} vs {qmatch2pick}\n{qmatch3pick} vs {qmatch4pick}",inline=True)
    championsEmbed.add_field(name="Semi-Finals",value=f"{smatch1pick} vs {smatch2pick}\n-",inline=True)
    championsEmbed.add_field(name="Grand Finalist",value=f"{cmatchpick}\n-",inline=True)
    championsEmbed.set_author(name="SourceCode",url="https://github.com/Brambler/Discord-CSGO-Pickem",icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",proxy_icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")
    championsEmbed.set_footer(text="Brambles Pickem Bot - Version {version}")



getChallengerPickemInfo(steam_api_key, event, users_steamid, user_auth_code)