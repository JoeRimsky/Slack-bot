# Author
Joseph Rimsky

## Purpose
The purpose of this Slack bot is to speed up daily observations by bringing multiple datasets to one source.

##  How?
The Slack bot utilizes Slack's *RTM API* [Real Time Messaging] to listen for keywords in messages. Once a keyword is detected, the message is parsed and the output is determined. A .yaml file is used to store spreadsheet_id's and ranges to be passed through Google's *Sheets API*. Specific channels are used to provide hourly updates [on the hour] with key data points through asynchronous processing.

## Instructions
User must specify the given Slack API token as an environment variable named "SLACK_TOKEN":  
`export SLACK_TOKEN=*Provided Slack token*`

Install required packages:  
`pip install -r requirements.txt`

Start Slack bot to begin listening for messages:  
`python rtm_bot.py`