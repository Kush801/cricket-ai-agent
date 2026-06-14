import requests
from bs4 import BeautifulSoup
import pandas as pd 
import time


Matches=[]
url="https://www.howstat.com/Cricket/Statistics/Matches/MatchList_ODI.asp?Group=2026010120261231&Range=2026"
response= requests.get(url)
soup= BeautifulSoup(response.content,"html.parser")
print("Page Size:",len(response.content),"bytes")

table = soup.find("table",class_="TableLined")
rows=table.find_all("tr")

seen=set()

for row in rows[1:]:
    cell=row.find_all("td")

    date=cell[1].text.strip()
    series=cell[2].text.strip()
    venue=cell[4].text.strip()
    result=cell[5].text.strip()

    if not date or not result:
        continue    
        
    teams=series.split("v.")
    if len(teams)==2:
        team1=" ".join(teams[0].split()[1:])
        team2=teams[1].strip()
    else:
        team1="unknown"
        team2="unknown"

    if "won" in result:
        winner=result.split("won")[0].strip()
    else:
        winner="No Result"

    duplicate=f"{date}-{team1}-{team2}-{venue}"
    if duplicate not in seen:
        seen.add(duplicate)
        Matches.append({
            "Date":date,
            "Team1":team1,
            "Team2":team2,
            "Venue":venue,
            "Winner":winner
     })
        if len(Matches)==10:
            break
for m in Matches:
    print(m) 

print("total rows found:",len (rows))

df=pd.DataFrame(Matches)
df.to_csv("match_data.csv",index=False)

print(df)