from sys import stderr
from bs4 import BeautifulSoup
from time import sleep
import requests
import discord

"""
Um pequeno script que fiz só para me notificar quando um componente fica disponivel na
pcdiga.
"""

def perror(msg):
    print(msg,file=stderr)

class Item:
    def __init__(self, name, url):
        self._available = [None]
        self._name = name
        self._url = url
    
    async def check(self):
        ret = available(self._url)
        if ret != self._available:
            self._available = ret
            await message(notify(self))

def notify(item):
    msg = "*** %s ***\n" % item._name
    if item._available == []:
        msg += "INDISPONIVEL\n"
    else:
        for pair in item._available:
            if(pair[1]):
                msg += "%s - DISPONIVEL\n" % pair[0]
    return msg

#o fake_userAgent não estava a conseguir fazer request entao está hard coded
hdr = {"user-agent":"Opera/8.58 (X11; Linux i686; en-US) Presto/2.11.274 Version/10.00",\
 "connection": "Keep-alive" }
 
client = discord.Client()

def available(url):

    def request(url):
        tries = 0
        while((res:=requests.get(url , headers=hdr)).status_code != 200):
            tries += 1
            sleep(0.5)
            if tries > 5:
                raise Exception() #lazy but works
        return res
                

    try:
        res = request(url)
    
    except Exception:
        perror("O request nao foi bem sucedido")
        return [("ERROR", "O request nao foi bem sucedido")]

    soup = BeautifulSoup(res.content, "html.parser")

    tags = soup.findAll("div", class_="store-stock-location")

    places = list()
    for tag in tags[1:]:
        places.append((tag.text.replace('\t', '').replace('\n', ''),tag.find('span').attrs["class"][1] == "icon-checkmark"))

    placesAvailable = list(filter(lambda pair : pair[1], places))
    
    return placesAvailable

if __name__ == "__main__":
    items = list()
    print("^D aborta o input e deixa o programa a correr")
    try:
        while((item:=input("url:\n>> ")) and (name:=input("\nNome\n>> "))):
            items.append(Item(name, item))
    except EOFError:
        print("\ndone")
        
    client.run("key")

#sujo mas eficaz
@client.event
async def on_ready():
    print('Bot Running')
    while(True):
        sleep(5)
        for item in items:
            await item.check()

async def message(message):
    await client.wait_until_ready()
    channelId = int() #channelID
    channel = client.get_channel(channelId)
    if channel:
        await channel.send(message)
    else:
        print("f")
