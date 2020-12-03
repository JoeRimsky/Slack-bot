#!/usr/bin/python3
import os, sys, time, yaml, asyncio, concurrent, schedule
import sheets_api
from slack import RTMClient
from slack import WebClient
from slack.errors import SlackApiError

SLACK_TOKEN = os.environ['SLACK_TOKEN']
YAML_FILE = yaml.load(open("config.yaml"), Loader=yaml.FullLoader)
# Created for scheduled messages
WEB_CLIENT = WebClient(token=SLACK_TOKEN)

# Listens for any message in a direct message to the bot or in a channel containing the bot
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
        valid_command = verify_command(message)

    if valid_command:
        subject = command.capitalize()
        request = get_request(username=username, command=message)

        if subject == "Help":
            text = request
        elif subject == "Logs":
            file_path = request
            filename = os.path.basename(file_path)
            filetype = "log"
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

# Verify passed message is a valid command for processing
def verify_command(message):
    commands = YAML_FILE["AVAILABLE_COMMANDS"]
    return message in commands

# Evaluate passed command to gather desired data
def get_request(username, command):
    response = ""
    scopes = YAML_FILE["SCOPES"]
    sheets_api_connection = sheets_api.connect_to_api(scopes=scopes)
    
    if command == 'HELP':
        response = YAML_FILE['RESPONSE'][command]['MESSAGE']
    elif command == 'LOGS':
        response = YAML_FILE['RESPONSE'][command]['FILE_PATH']
    else:
        spreadsheet_id = YAML_FILE['RESPONSE'][command]['URL']
        sheet_range = YAML_FILE['RESPONSE'][command]['RANGE']
        optional_range = YAML_FILE['RESPONSE'][command].get('OPT_RANGE', None)
        response = sheets_api.get_data(username=username,message=command,service=sheets_api_connection,spreadsheet_id=spreadsheet_id,sheet_range=sheet_range,optional_range=optional_range)
  
    return response

# Step through SCHEDULED_MESSAGES in config.yaml to gather channels and commands to be sent every hour
def scheduled_message():
    scheduled_messages = YAML_FILE["SCHEDULED_MESSAGES"]
    for scheduled in scheduled_messages.keys():
        channel = scheduled_messages[scheduled]["CHANNEL"]
        command = scheduled_messages[scheduled]["COMMAND"]

        subject = command.capitalize()
        request = get_request(username='Bot',command=command)

        WEB_CLIENT.chat_postMessage(
            channel=channel,
            text=f"*{subject}* :bossanova: \n```{request}```"
        )

# Create an hourly schedule between 2:00 and 18:00 machine time
def sync_loop():
    for x in range(2, 19):
        time_string = f"{x:02d}:00"
        schedule.every().day.at(time_string).do(scheduled_message)

    while True:
        schedule.run_pending()
        time.sleep(1)

# Main function to initiate webhook for RTM API and create scheduler for scheduled messages
async def main():
    loop = asyncio.get_event_loop()
    rtm_client = RTMClient(token=SLACK_TOKEN, run_async=True, loop=loop)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    await asyncio.gather(
        loop.run_in_executor(executor, sync_loop),
        rtm_client.start()
    )

if __name__ == "__main__":
    asyncio.run(main())