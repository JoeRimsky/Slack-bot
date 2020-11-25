*AUTHOR*: Joseph Rimsky  

# Purpose
The purpose of this Slack bot is to speed up daily observations by bringing multiple datasets to one source.

##  How?
The Slack bot utilizes Slack's *RTM API* [Real Time Messaging] to listen for keywords in messages. Once a keyword is detected, the message is parsed and the output is determined. A .yaml file is used to store spreadsheet_id's and ranges to be passed through Google's *Sheets API*. Specific channels are used to provide hourly updates [on the hour] with key data points through asynchronous processing.

## Requirements
User must specify the given Slack API token as an environment variable named "SLACK_TOKEN"