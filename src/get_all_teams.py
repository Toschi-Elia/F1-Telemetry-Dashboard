import requests 

def extract_all_team():
    print("Scaricamento di tutti i dati dei piloti in corso... attendere...")

    url = "https://api.openf1.org/v1/drivers"

    response= requests.get(url) 

    if response.status_code==200:
        data = response.json()

        teams= set()

        for record in data:
            if "team_name" in record and record["team_name"] is not None:
                teams.add(record["team_name"])

        print("\n--- TUTTI I TEAM REGISTRATI IN OPENF1 ---")     

        for team in sorted(list(teams)):
                print(f'"{team}": "???",')
         
    else:
        print(f"Errore API: {response.status_code}")  


if __name__ == "__main__":
    extract_all_team()