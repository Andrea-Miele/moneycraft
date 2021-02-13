#from numba import jit, int32, float32
#from numba.experimental import jitclass
import os
#import tornado
#import tornado.websocket
#import tornado.web
import re
html = '''
<html>
    <head>
    <title>Moneycraft </title>
    </head>
    <body>
    <h3 style="color:gold; font-size:60px;" >Moneycraft </h3>
    <p><em>Moneycraft is an addon/websocket for minecraft bedrock/pe that allows to use money in minecraft.</em></p>
    <a href="download"> <button>Download</button></a>
    </body>
</html>
'''
'''
spec = [
    ('value', int32),               # a simple scalar field
    ('array', float32[:]),          # an array field
]
'''
###################################
#@jitclass(spec)
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(html)
#@jitclass
class FileHandler(tornado.web.RequestHandler):
    def get(self):
        ifile  = open("moneycraft-websocket", "r")
        self.set_header ('Content-Type', 'text/py')
        self.set_header ('Content-Disposition', 'attachment; filename=main.py')
        self.write (ifile.read())
###################################
def send_command(command):
    cmd = {"body": {"origin": {"type": "player"},"commandLine": command,"version": 1},"header": {"requestId": "00000000-0000-0000-0000-000000000000","messagePurpose": "commandRequest", "version": 1,"messageType": "commandRequest" }}
    WSHandler.mcws.write_message(cmd)

#@jitclass(spec)
class event():
    def on_message(self, message, player):
        command = ''' scoreboard players test "%s" money * *''' % (player)
        print(command)
        send_command(command)
    def on_command(self, message,player):
        lista = re.findall(r'\d+',message)
        number = lista[0]
        command = '''/tellraw "%s" {"rawtext":[{"text":"You have %s money"}]}''' % (player,number)
        send_command(command)
    def addmoney(self, message,player):
        command = ''' scoreboard players add "%s" money %s''' % (player,message)
        send_command(command)
        command = '''/tellraw "%s" {"rawtext":[{"text":"Added %s money to your count"}]}''' % (player,message)
        send_command(command)
    def removemoney(self, message,player):
        command = ''' scoreboard players remove "%s" money %s''' % (player,message)
        send_command(command)
        command = '''/tellraw "%s" {"rawtext":[{"text":"Added %s money to your count"}]}''' % (player,message)
        send_command(command)
############ EVENT LIST ##############
eventlist = ["PlayerMessage"]
######################################

############# Websocket Connect Event #########
#@jitclass(spec)
class WSHandler(tornado.websocket.WebSocketHandler):
  mcws = None
  def open(self):
    for event in eventlist:
        event = {"body": {"eventName": event},"header": {"requestId": "00000000-0000-0000-0000-000000000000","messagePurpose": "subscribe","version": 1,"messageType": "commandRequest"}}
        self.write_message(event)
        WSHandler.mcws = self


################################################



############ MINECRAFT CALLBACK EVENTS##############
  def on_message(self, message):
    try:
        packagew = json.loads(message)
        print(packagew)
    except:
        print("Make Sure You Connected To Minecraft Not Normal Websocket Client.")
    try:
        if packagew["body"]["properties"]["MessageType"] == "chat" and packagew["body"]["properties"]["Message"] == "*/showmoney":
            message = None
            player = packagew["body"]["properties"]["Sender"]
            event.on_message(message,player)
    except:
        pass
    try:
        if packagew["body"]["statusCode"] == 0 and packagew["body"]["statusMessage"] != "":
            message = packagew["body"]["statusMessage"]
            event.on_command(message,player)
    except:
        pass
    try:
        if packagew["body"]["properties"]["MessageType"] == "chat" and packagew["body"]["properties"]["Message"].startswith("*/addmoney") == True:
            message_string = packagew["body"]["properties"]["Message"]
            message_list = message_string.split()
            message = message_list[1]
            player = packagew["body"]["properties"]["Sender"]
            event.addmoney(message,player)
    except:
        pass
    try:
        if packagew["body"]["properties"]["MessageType"] == "chat" and packagew["body"]["properties"]["Message"].startswith("*/removemoney") == True:
            message_string = packagew["body"]["properties"]["Message"]
            message_list = message_string.split()
            message = message_list[1]
            player = packagew["body"]["properties"]["Sender"]
            event.removemoney(message,player)
    except:
        pass
###############################################



##########CLOSE EVENT + START SERVER ##########
  def on_close(self):
    print('connection closed...')
#@jit
def main():
    import tornado
    import tornado.web
    import tornado.websocket
    print("use /connect 127.0.0.1:8080/ws ingame")
    application = tornado.web.Application([
        (r'/ws', WSHandler),
        (r'/' , MainHandler),
        (r'/download', FileHandler)
        ])
    application.listen(int(os.environ.get("PORT", 8080)))
    tornado.ioloop.IOLoop.instance().start()
################################################
import micropip
    micropip.install('tornado').then(main)
