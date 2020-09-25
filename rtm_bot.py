#!/usr/bin/python3
import os
import sys
import time
import sheets_api
import yaml
import asyncio
import concurrent
import schedule
from slack import RTMClient
from slack import WebClient
from slack.errors import SlackApiError

YAML_FILE = yaml.load(open("config.yaml"), Loader=yaml.FullLoader)
WEB_CLIENT = WebClient(token=YAML_FILE["SLACK_TOKEN"])
DEFAULT_CHANNEL = 'ops-metrics'
HIGH_VIS_CHANNEL = 'hivizstores'

@RTMClient.run_on(event='message')
async def handle_message(**payload):
  data = payload['data']
  web_client = payload['web_client']

  if 'text' in data:
    message = data.get('text',[]).upper()
    channel_id = data['channel']
    user = data['user']
    text = ""

    sheet_data, request = parse_message(message, user)

    if request == "Help":
      text = YAML_FILE["HELP"].get('MESSAGE', None)
    if request and request != "Help":
      text = f"Hi <@{user}>!\n*{request} Data* :bossanova: \n```{sheet_data}```"
    
    if request:
      try:
        web_client.chat_postMessage(
          channel=channel_id,
          text=text
        )
      except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")

@RTMClient.run_on(event='hello')
async def handle_hello(**payload):
  print("Hello!")

  #web_client = payload['web_client']
  #try:
  #  web_client.chat_postMessage(
  #    channel=DEFAULT_CHANNEL,
  #    text=f"Hello! I am now active and ready to take requests!"
  #  )
  #except SlackApiError as e:
  #  assert e.response["ok"] is False
  #  assert e.response["error"]
  #  print(f"Got an error: {e.response['error']}")

def parse_message(message, user):
  scopes = YAML_FILE["SCOPES"]
  sheets_api_connection = sheets_api.connect_to_api(scopes)
  if message == 'METRICS':
    print(user, 'requested:', message)
    request = "Metrics"

    spreadsheet_id = YAML_FILE["TIMELINE"].get('URL', None)
    sheet_range = YAML_FILE["TIMELINE"].get('RANGE', None)
    response = sheets_api.get_data(sheets_api_connection, spreadsheet_id, sheet_range)
  elif message == 'KLIPFOLIO':
    print(user,'requested:', message)
    request = "Klipfolio"

    spreadsheet_id = YAML_FILE["KLIPFOLIO"].get('URL', None)
    sheet_range = YAML_FILE["KLIPFOLIO"].get('RANGE', None)
    response = sheets_api.get_data(sheets_api_connection, spreadsheet_id, sheet_range)
  elif message == 'SLA':
    print(user,'requested:', message)
    request = "SLA"

    spreadsheet_id = YAML_FILE["SLA"].get('URL', None)
    sheet_range = YAML_FILE["SLA"].get('RANGE', None)
    response = sheets_api.get_data(sheets_api_connection, spreadsheet_id, sheet_range)
  elif message == '6 STORE':
    print(user,'requested:', message)
    request = "6 store"

    spreadsheet_id = YAML_FILE["TIMELINE"].get('URL', None)
    sheet_range = YAML_FILE["TIMELINE"].get('SPEC_STORE_DATA', None)
    optional_range = YAML_FILE["TIMELINE"].get('SPEC_STORE_STATUS', None)
    response = sheets_api.get_data(sheets_api_connection, spreadsheet_id, sheet_range, optional_range)
  elif message == 'HELP':
    print(user, 'requested:',message)
    request = "Help"
    response = YAML_FILE["HELP"].get('MESSAGE', None) 
  else:
    response = ""
    request = ""

  return response, request

def delete_messages():
  return

def scheduled_message():
  sheet_data, request = parse_message('METRICS','Bot')
  WEB_CLIENT.chat_postMessage(
    channel=DEFAULT_CHANNEL,
    text=f"*{request} Data* :bossanova: \n```{sheet_data}```"
  )
  sheet_data, request = parse_message('6 STORE','Bot')
  WEB_CLIENT.chat_postMessage(
    channel=HIGH_VIS_CHANNEL,
    text=f"*{request} Data* :bossanova: \n```{sheet_data}```"
  )

def testing_job():
  print("In testing")

def sync_loop():
  schedule.every().hour.at(":00").do(scheduled_message)
#  schedule.every(3).seconds.do(testing_job)
  while True:
    schedule.run_pending()
    time.sleep(1)

async def main():
  loop = asyncio.get_event_loop()
  rtm_client = RTMClient(token=YAML_FILE["SLACK_TOKEN"], run_async=True, loop=loop)
  executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
  await asyncio.gather(
    loop.run_in_executor(executor, sync_loop),
    rtm_client.start()
  )

if __name__ == "__main__":
  asyncio.run(main())
