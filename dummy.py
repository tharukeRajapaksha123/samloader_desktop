import requests
from bs4 import BeautifulSoup

samMobileReq = requests.get("https://www.sammobile.com/firmwares/")
smasungReq = requests.get("https://samfrew.com/")
soup = BeautifulSoup(samMobileReq.content,"html.parser")
samSoup = BeautifulSoup(smasungReq.content,"html.parser")

aLinks = soup.find_all("a", {"class": "table-link"})

available_list = []


for link in aLinks:
    available_list.append(link.get_text())









