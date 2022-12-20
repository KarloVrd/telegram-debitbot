# -*- coding: UTF8 -*-
import requests
import json
import os
from DynamoDBDataClass import DynamoDBDataClass

from DebitHandler import DebitHandler
from CustomCommandsHandler import CCHandler

TOKEN = os.environ["TELEGRAM_TOKEN"]
url = "https://api.telegram.org/bot{}/".format(TOKEN)

testerId = 1217535067

t = DynamoDBDataClass()
DH = DebitHandler(t)
CC = CCHandler()

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

def reply_to_message(chat_id, text, message_id, parse_mode="HTML"):
    params = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "reply_to_message_id": message_id}
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
        sender_id = event["message"]["from"]["id"]

        if testMode:
            if sender_id != testerId:
                msg_out = "Maintenance mode, try again later"
                reply_to_message(chat_id = chat_id, text = msg_out, message_id = message_id)
                return False

        message = (
            event["message"]["text"]
            .split("#")[0]
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("\t", " ")
            .replace("\xa0", " ")
            .split(" ")
        )
        
        message = [i for i in message if i != ""]

        # remove '/' from command
        command_code = message[0][1:]
        args = message[1:]
        command = " ".join(message)[1:]

        # custom_commands = CC.load_custom_commands()
        # debit commands
        if command_code in DH.commands:
            msg_out = DH.commands_API(command_code=command_code, args=args, chat_id=chat_id)
            t.save_log(command=command,sender_id=sender_id,chat_id=chat_id)

        # # custom command
        # elif command_code in custom_commands:
        #     msg_out = custom_commands[command_code]

        # # handle custom commands
        # elif command_code in CC.commands:
        #     msg_out = CC.commands_API(command_code, args)

        else:
            msg_out = "Unknown command"
        #send_message(chat_id = chat_id, text = msg_out)
        reply_to_message(chat_id = chat_id, text = msg_out, message_id = event["message"]["message_id"])

    except Exception as e:  #    ERROR
        # check if error is from DebitHandler
        if type(e) in DH.exceptions_list:
            msg_out = str(e)
        else:
            if testMode:
                #pass
                raise e
            msg_out = "I'm sorry, Dave. I'm afraid I can't do that."
            msg_out = "Invalid command"
                 
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
        # send aws event
        # aws_lambda_handler(event = json.loads(open("event.json", "r").read()), context = None)

        send_message(testerId, "Bot started")
        ap = BotApi()
        print("Start")
        while True:
            ap.process_updates(timeout = 30 , testMode=True)
    except KeyboardInterrupt:
        exit()