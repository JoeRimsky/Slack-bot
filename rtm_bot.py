#!/usr/bin/python3
import os, sys, time, yaml, asyncio, concurrent, schedule, logging
import sheets_api
from slack import RTMClient
from slack import WebClient
from slack.errors import SlackApiError

YAML_FILE = yaml.load(open("config.yaml"), Loader=yaml.FullLoader)
WEB_CLIENT = WebClient(token=YAML_FILE["SLACK_TOKEN"])

@RTMClient.run_on(event='message')
async def handle_message(**payload):
  data = payload['data']
  web_client = payload['web_client']

  if 'text' in data:
    message = data.get('text',[]).upper()
    channel_id = data['channel']
    user = data['user']
    user_info = WEB_CLIENT.users_info(user=user)
    username = user_info['user']['real_name']
    text = ""

    request, subject = parse_message(username=username, message=message)

    if subject == "Help":
      text = request
    elif subject == "Logs":
      file_path = request
      filename = os.path.basename(file_path)
      filetype = "log"
    elif subject == "Goodbye":
      text = request
      channel_id = YAML_FILE["CHANNELS"].get('DEFAULT', None)
    elif subject and subject != "Help":
      text = f"Hi <@{user}>!\n*{subject}* :bossanova: \n```{request}```"
    
    if subject and subject != "Logs":
      try:
        web_client.chat_postMessage(
          channel=channel_id,
          text=text
        )
      except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
    elif subject == "Logs":
      try:
        web_client.files_upload(
          channels=channel_id,
          file=file_path,
          title=filename,
          filetype=filetype
        )
      except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]

@RTMClient.run_on(event='hello')
async def handle_hello(**payload):
  return

def parse_message(username, message):
  scopes = YAML_FILE["SCOPES"]
  commands = YAML_FILE["AVAILABLE_COMMANDS"]
  sheets_api_connection = sheets_api.connect_to_api(scopes=scopes)
  subject = ""
  response = ""

  if message == 'GOODBYE':
    subject = message.capitalize()
    response = '_The 6PM update will be my last alert. Thank you everyone for utilizing my services._'

  if message in commands:
    subject = message.capitalize()

    if message == 'HELP':
      response = YAML_FILE['RESPONSE'][message]['MESSAGE']
    elif message == 'LOGS':
      response = YAML_FILE['RESPONSE'][message]['FILE_PATH']
    else:
      spreadsheet_id = YAML_FILE['RESPONSE'][message]['URL']
      sheet_range = YAML_FILE['RESPONSE'][message]['RANGE']
      optional_range = YAML_FILE['RESPONSE'][message].get('OPT_RANGE', None)
      response = sheets_api.get_data(username=username,message=message,service=sheets_api_connection,spreadsheet_id=spreadsheet_id,sheet_range=sheet_range,optional_range=optional_range)
  
  return response, subject

# Adjust this to loop through the list of channels and desired data sets
# Put additional data set level under each channel on yaml file
def scheduled_message():
  #channels = YAML_FILE["CHANNELS"]

  sheet_data, request = parse_message(message='METRICS',username='Bot')
  WEB_CLIENT.chat_postMessage(
    channel=YAML_FILE["CHANNELS"].get('DEFAULT', None),
    text=f"*{request}* :bossanova: \n```{sheet_data}```"
  )
  sheet_data, request = parse_message(message='6 STORE',username='Bot')
  WEB_CLIENT.chat_postMessage(
    channel=YAML_FILE["CHANNELS"].get('HIVIZ', None),
    text=f"*{request}* :bossanova: \n```{sheet_data}```"
  )

def sync_loop():
  schedule.every().day.at("02:00").do(scheduled_message)
  schedule.every().day.at("03:00").do(scheduled_message)
  schedule.every().day.at("04:00").do(scheduled_message)
  schedule.every().day.at("05:00").do(scheduled_message)
  schedule.every().day.at("06:00").do(scheduled_message)
  schedule.every().day.at("07:00").do(scheduled_message)
  schedule.every().day.at("08:00").do(scheduled_message)
  schedule.every().day.at("09:00").do(scheduled_message)
  schedule.every().day.at("10:00").do(scheduled_message)
  schedule.every().day.at("11:00").do(scheduled_message)
  schedule.every().day.at("12:00").do(scheduled_message)
  schedule.every().day.at("13:00").do(scheduled_message)
  schedule.every().day.at("14:00").do(scheduled_message)
  schedule.every().day.at("15:00").do(scheduled_message)
  schedule.every().day.at("16:00").do(scheduled_message)
  schedule.every().day.at("17:00").do(scheduled_message)
  schedule.every().day.at("18:00").do(scheduled_message)
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