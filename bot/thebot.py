'''
BOT FUNCTIONAL SCRIPT
CREATED BY FRBELLO AT CISCO DOT COM
DATE JUN 2018
VERSION 1.0
STATE RC1
DESCRIPTION:
This is the script hosting all the logic for the bot to hears calls from the webhook
this will be publish the GET and POST methods for spark bot.
'''

#Libraries
#========= microframeworks ====================
from flask import Flask, request, render_template as template, make_response, jsonify, abort

#======== Common Libraries ====================
import re, json
import requests
import os,sys

from requests_toolbelt.multipart.encoder import MultipartEncoder

#Import CiscoSparkAPI()
from ciscosparkapi import CiscoSparkAPI,Webhook

#Import Logging
import logging
import logging.handlers
from datetime import datetime

#Global Variables
global bot_tkn
global bot_email
global bot_name
global bot_id


#Token Retrieve
bot_id = str(os.environ['BOT_ID'])
bot_email = str(os.environ['BOT_EMAIL'])
bot_name = str(os.environ['BOT_NAME'])
bot_tkn = str(os.environ['SPARK_ACCESS_TOKEN'])


#========== Versioning ==============
__author__ = "Freddy Bello"
__author_email__ = "frbello@cisco.com"
__copyright__ = "Copyright (c) 2016-2018 Cisco and/or its affiliates."
__license__ = "MIT"


#===== Bot Functions ==============
class theBot:
    def __init__ (self):
        self.botName = bot_name
        self.botEmail = bot_email
        self.botTkn = bot_tkn
        self.botId =  bot_id
        self.Commands = {}
        try:
            self.botAPI = CiscoSparkAPI()
        except (ValueError) as e:
            self.botAPI = None 

    def CommandList(self):
        self.Commands = { "/echo" : "Reply with the same message",
                          "/help" : "Get This help",
                          "/cmx" : "Display active connections on CMX"
                        }

        return ""   

    def ProcessInMessage(self,post_data):
        '''
        Handle Webhook Data
        '''
        
        #Determine the Wbx Team Room to send the mesage
        room_id = post_data['data']['roomId']

        #Get Message Details
        message_id = post_data['data']['id']
        message = self.botAPI.messages.get(message_id)

        #Make sure not processing a message from the bot
        if message.personEmail in self.botAPI.people.me().emails:
            return ""

        #Log Details on Message
        sys.stderr.write("Message from: " + message.personEmail + "\n")

        #Find the Order to Execute
        command = ""
        self.CommandList()
        for item in self.Commands.items():
            if message.text.find(item[0]) != -1: #The message contains a command from the list
                command = item[0]
                sys.stderr.write("found command: " + command +  "\n")
                break  #Stop when a command is found

        #Take an Action if no command, then send help
        reply = ""
        if command in ["","/help"]:
            reply =  self.SendHelp()
        elif command in ["/echo"]:
            reply =  self.SendEcho(message.text)
        elif command in ["/cmx"]:
            reply = self.SendCMX()
         
    
        
        self.botAPI.messages.create(roomId=room_id,markdown=reply) 
   
     
    def SendHelp(self):
        '''
        Build a Help Message
        '''
        reply = "This are the current supported commands:  \n" 
        for item in self.Commands.items():
            reply =  reply + "**"+item[0] + "** - " +  item[1] + "\n\n" 

        return reply
    

    def SendEcho(self,message):
        '''
        Echo Bot
        '''
        reply = message[6:] 
       

        return reply

    def SendCMX(self):
        cmxUSR =  str(os.environ['CMX_USR'])
        cmxPAS =  str(os.environ['CMX_PAS'])
        cmxURI =  str(os.environ['CMX_URI'])


        endpoint = 'https://'+ cmxURI + 'v3/clients/count'
        r = requests.get(endpoint,auth=(cmxUSR,cmxPAS),verify=False)

        data = json.loads(r.text)

        reply = ''' 
                 This is the response from **{0}**\n
                -Total Count : **{1}** \n
                -Clients Associated : **{2}** \n\n
                '''.format(cmxURI,data["totalCount"],data['associatedCount'])
        

        return reply

#############################################
#  W E B H O O K    E N D P O I N T 
############################################
#========= Flask Instance ==============
app = Flask(__name__)

#========= Flask GET URI Methods ===================

@app.route('/bot/v1/base/')
def test_uri():
    return "<h1>Bot Served by Flasks</h1>"


#========== Flask POST URI Methods =============

'''
Main Endpoint
'''

@app.route('/bot/', methods=['POST'])
def process_webhook():

    
    bot = theBot()
    post_data = request.get_json(force=True)
  
    bot.ProcessInMessage(post_data)
    
 
    return ""


