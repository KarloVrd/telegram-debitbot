# -*- coding: UTF8 -*-
import traceback
import requests
import time

from DebitHandler import DebitHandler
from CustomCommandsHandler import CCHandler
from LogsHandler import LogsHandler


class BotHandler:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"

    def get_updates(self, offset=0, timeout=30, verify=False):  # 30
        method = "getUpdates"
        params = {"timeout": timeout, "offset": offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()["result"]
        return result_json

    def send_message(self, chat_id, text):
        params = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        method = "sendMessage"
        resp = requests.post(self.api_url + method, params)
        return resp

    def reply_to_message(self, chat_id, text, message_id):
        params = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "reply_to_message_id": message_id}
        method = "sendMessage"
        resp = requests.post(self.api_url + method, params)
        return resp

def security_check(update):
    return True

    secure_chat_ids = [1217535067, -518192732, -1001172051071, -568705610]
    if update["message"]["chat"]["id"] in secure_chat_ids:
        return True
    return False

def prijeteca_poruka(num):
    poruke = [
        "Hehe...",
        "Ocekivao sam te...",
        "Glupane...",
        "Sace ti moji zabijaci dugova dug zabit... ",
    ]
    for i in poruke:
        magnito_bot.send_message(num, i)
        time.sleep(2)

def prijeteca_poruka_grupa(offset):
    poruke = ["Hehe...", "Dobar pokusaj...", "Seto jedno...",]
    for i in poruke:
        magnito_bot.send_message(offset, i)
        time.sleep(2)

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
        return False

    return True

token = "1647743462:AAFcjy2b-PhRiYN2z9dkMhTwNgEfD3mPreY"  # Token of your bot
magnito_bot = BotHandler(token)  # Your bot's name
testerId = 1217535067

DH = DebitHandler()
CC = CCHandler()
LH = LogsHandler()
print("Start")


class BotApi:
    def __init__(self):
        self.new_offset = 0

    def process_updates(self, timeout=30, testMode=False):
        all_updates = magnito_bot.get_updates(self.new_offset, timeout=timeout)

        if len(all_updates) == 0:
            return False

        for current_update in all_updates:
            try:
                show(current_update)

                current_update_id = current_update["update_id"]
                self.new_offset = current_update_id + 1

                if filter_update(current_update) == False:
                    continue

                chat_id = current_update["message"]["chat"]["id"]
                message_id = current_update["message"]["message_id"]

                if testMode:
                    if current_update["message"]["from"]["id"] != testerId:
                        msg_out = "Bot has better things to do. Try again later."
                        magnito_bot.reply_to_message(chat_id = chat_id, text = msg_out, message_id = message_id)
                        continue

                update_text = (
                    current_update["message"]["text"][1:]
                    .split("#")[0]
                    .replace("\n", " ")
                    .replace("\r", " ")
                    .replace("\t", " ")
                    .replace("\xa0", " ")
                    .split(" ")
                )
                
                update_text = [i for i in update_text if i != ""]
                current_update["message"]["text"] = " ".join(update_text)

                if "title" in current_update["message"]["chat"]:
                    title = current_update["message"]["chat"]["title"].replace(" ", "_")
                else:
                    title = get_user_name(current_update)

                in_dict = {
                    "comm": update_text[0].lower(),
                    "args": update_text[1:],
                    "id": current_update["message"]["chat"]["id"],
                    "title": title,
                }
            
                custom_commands = CC.load_custom_commands()

                # komande za dugove
                if in_dict["comm"] in DH.commands:
                    msg_out = DH.commands_API(in_dict)
                    LH.save_input(current_update)

                # komande za sprdačinu
                elif in_dict["comm"] in custom_commands:
                    msg_out = custom_commands[in_dict["comm"]]
                    LH.save_input(current_update)

                # komande za upravljanje sprdačina
                elif in_dict["comm"] in CC.commands:
                    msg_out = CC.commands_API(in_dict)
                    LH.save_input(current_update)

                else:
                    msg_out = "Unknown command"
                
                magnito_bot.reply_to_message(chat_id = chat_id, text = msg_out, message_id = current_update["message"]["message_id"])

            except FileExistsError as e:  #    ERROR
                print(e)
                traceback.print_exc()

                msg_out = "Invalid command"
                magnito_bot.reply_to_message(chat_id = chat_id, text = msg_out, message_id = current_update["message"]["message_id"])

        return True
    
    def load_chat_history(self):
        pass

if __name__ == "__main__":
    try:
        ap = BotApi()
        while True:
            ap.process_updates(timeout = 30 , testMode=True)
    except KeyboardInterrupt:
        exit()