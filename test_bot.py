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

@RTMClient.run_on(event='message')
async def handle_message(**payload):
  data = payload['data']
  web_client = payload['web_client']

  if 'text' in data:
    message = data.get('text',[]).upper()
    user = data['user']

    sheet_data, request = parse_message(message, user)

    if not request:
      try:
        web_client.chat_postMessage(
          channel='ULPHLCEVD',
          text=f"Hi <@{user}>!\n*{request} Data* :bossanova: \n```{sheet_data}```"
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
  sheet_data = [], request = ""
  if 'METRICS' in message:
    print(user, 'requested:', message)
    request = "Metrics"

    spreadsheet_id = YAML_FILE["TIMELINE"].get('URL', None)
    sheet_range = YAML_FILE["TIMELINE"].get('RANGE', None)
    sheet_data = sheets_api.get_data(sheets_api_connection, spreadsheet_id, sheet_range)
  elif 'KLIPFOLIO' in message:
    print(user,'requested:', message)
    request = "Klipfolio"

    spreadsheet_id = YAML_FILE["KLIPFOLIO"].get('URL', None)
    sheet_range = YAML_FILE["KLIPFOLIO"].get('RANGE', None)
    sheet_data = sheets_api.get_data(sheets_api_connection, spreadsheet_id, sheet_range)
  elif 'SLA' in message:
    print(user,'requested:', message)
    request = "SLA"

    spreadsheet_id = YAML_FILE["SLA"].get('URL', None)
    sheet_range = YAML_FILE["SLA"].get('RANGE', None)
    sheet_data = sheets_api.get_data(sheets_api_connection, spreadsheet_id, sheet_range)
  elif '6 STORE' in message:
    print(user,'requested:', message)
    request = "6 store"

    spreadsheet_id = YAML_FILE["TIMELINE"].get('URL', None)
    sheet_range = YAML_FILE["TIMELINE"].get('SPEC_STORE_DATA', None)
    sheet_data = sheets_api.get_data(sheets_api_connection, spreadsheet_id, sheet_range)

  return sheet_data, request

def scheduled_message():
  channel = DEFAULT_CHANNEL
  sheet_data, request = parse_message('Metrics','Bot')
  WEB_CLIENT.chat_postMessage(
    channel=channel,
    text=f"*{request} Data* :bossanova: \n```{sheet_data}```"
  )

def sync_loop():
  schedule.every().hour.do(scheduled_message)
  while True:
    schedule.run_pending()
    time.sleep(1800)

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