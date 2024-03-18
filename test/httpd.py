import json
import requests
from socket import gethostbyname, gethostname
requests.packages.urllib3.disable_warnings()

#data = "data"
#notification = "notification"
#profile = {"profile": "cdcadcef41f44cf78991f711eb183681"}
#data = {"data":{"parameter3": "not value3"}}
#notification = {"notification":{"title3": "not message3"}}
#profile = {"profile": {"UUID": "HELLOWORLD", "name": "FDSFAS", "description": ""}}
data = {"data":"parameter2"}
notification = {"notification":"title2"}
profile = {"profile": "248873a9a15249c68a5fab1100772609"}

iplink = gethostbyname(gethostname())
server = 'https://' + iplink + ':443'


r = requests.get(server, verify=False, params=profile)
print(r.text)
r = requests.get(server, verify=False, params=data)
print(r.text)
r = requests.get(server, verify=False, params=notification)
print(r.text)
#r = requests.post(server, verify=False, json=data)
#print(r.text)
#r = requests.post(server, verify=False, json=notification)
#print(r.text)
#r = requests.post(server, verify=False, json=profile)
#print(r.text)

