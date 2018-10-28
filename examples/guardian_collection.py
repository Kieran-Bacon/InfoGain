import requests
from bs4 import BeautifulSoup
import uuid

content = requests.request("GET", "https://www.theguardian.com/football")


soup = BeautifulSoup(content.content, "html.parser")


a = soup.find_all('a', href=True)


valid = set()
for element in a:
    ref = element["href"]

    if r"https://www.theguardian.com/football" not in ref:
        continue

    valid.add(ref)

for i in valid:


    
    req = requests.request("GET", i)

    page = BeautifulSoup(req.content, "html.parser")

    contents = page.find_all("p")

    with open(str(uuid.uuid4()), "w") as handler:
        for p in contents:
            handler.write(p.text)


