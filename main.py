# -*- coding: UTF8 -*-
import traceback
import requests
import json
import os, sys

from DebitHandler import DebitHandler
from CustomCommandsHandler import CCHandler
from LogsHandler import LogsHandler

TOKEN = os.environ["TELEGRAM_TOKEN"]
url = "https://api.telegram.org/bot{}/".format(TOKEN)

testerId = 1217535067

DH = DebitHandler()
CC = CCHandler()
LH = LogsHandler()

def get_updates(offset=0, timeout=30):  # 30
    method = "getUpdates"
    params = {"timeout": timeout, "offset": offset}
    resp = requests.get(url + method, params)
    result_json = resp.json()["result"]
    return result_json

def send_message(chat_id, text):
    params = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    method = "sendMessage"
    resp = requests.post(url + method, params)
    return resp

def reply_to_message(chat_id, text, message_id):
    params = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "reply_to_message_id": message_id}
    method = "sendMessage"
    resp = requests.post(url + method, params)
    return resp

def get_user_name(current_update):
    if "username" in current_update["message"]["from"]:
        user = current_update["message"]["from"]["username"]
    elif "first_name" in current_update["message"]["from"] and "last_name" in current_update["message"]["from"]:
        first_name = current_update["message"]["from"]["first_name"]
        last_name = current_update["message"]["from"]["last_name"]
        user = f"{first_name} {last_name}"
    elif "first_name" in current_update["message"]["from"]:
        user = current_update["message"]["from"]["first_name"]
    else:
        return None
    return user

def show(current_update):
    if "message" not in current_update or "text" not in current_update["message"]:
        print("Missing message")
        return

    user = get_user_name(current_update)
    chat_id = current_update["message"]["chat"]["id"]
    text = current_update["message"]["text"]

    print(f"{chat_id}: {user} - {text}")


def filter_update(update):
    if "message" not in update or "text" not in update["message"] or update["message"]["text"][0] != "/":
        return True

    return False

def aws_lambda_handler(event, context):
    if isinstance(event, str):
        event = json.loads(event)
    update = event["body"]
    process_event(update)
    return {"statusCode": 200}

# for AWS Lambda to work, needs one function to be called
def process_event(event, testMode=False):
    try:
        if filter_update(event):
            return

        chat_id = event["message"]["chat"]["id"]
        message_id = event["message"]["message_id"]

        if testMode:
            if event["message"]["from"]["id"] != testerId:
                msg_out = "Maintenance mode, try again later"
                reply_to_message(chat_id = chat_id, text = msg_out, message_id = message_id)
                return

        update_text = (
            event["message"]["text"][1:]
            .split("#")[0]
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("\t", " ")
            .replace("\xa0", " ")
            .split(" ")
        )
        
        update_text = [i for i in update_text if i != ""]
        event["message"]["text"] = " ".join(update_text)

        if "title" in event["message"]["chat"]:
            title = event["message"]["chat"]["title"].replace(" ", "_")
        else:
            title = get_user_name(event)

        in_dict = {
            "comm": update_text[0].lower(),
            "args": update_text[1:],
            "id": event["message"]["chat"]["id"],
            "title": title,
        }
    
        custom_commands = CC.load_custom_commands()
        # debit commands
        if in_dict["comm"] in DH.commands:
            msg_out = DH.commands_API(in_dict)
            LH.save_input(event)

        # custom command
        elif in_dict["comm"] in custom_commands:
            msg_out = custom_commands[in_dict["comm"]]
            LH.save_input(event)

        # handle custom commands
        elif in_dict["comm"] in CC.commands:
            msg_out = CC.commands_API(in_dict)
            LH.save_input(event)

        else:
            msg_out = "Unknown command"
        
        reply_to_message(chat_id = chat_id, text = msg_out, message_id = event["message"]["message_id"])

    except Exception as e:  #    ERROR
        if testMode:
            pass
            #traceback.format_exc()
        msg_out = "I'm sorry, Dave. I'm afraid I can't do that."
        msg_out = str(e)
        
        reply_to_message(chat_id = chat_id, text = msg_out, message_id = event["message"]["message_id"])


class BotApi:
    def __init__(self):
        self.new_offset = 0

    def process_updates(self, timeout=30, testMode=False):
        all_updates = get_updates(self.new_offset, timeout=timeout)

        if len(all_updates) == 0:
            return False

        for current_update in all_updates:
            if testMode:
                show(current_update)
            process_event(current_update, testMode=testMode)
            current_update_id = current_update["update_id"]
            self.new_offset = current_update_id + 1

        return True

if __name__ == "__main__":
    try:
        send_message(testerId, "Bot started")
        ap = BotApi()
        print("Start")
        while True:
            ap.process_updates(timeout = 30 , testMode=True)
    except KeyboardInterrupt:
        exit()