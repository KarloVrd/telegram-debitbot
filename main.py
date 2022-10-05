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
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    # url = "https://api.telegram.org/bot1647743462:AAFcjy2b-PhRiYN2z9dkMhTwNgEfD3mPreY/getUpdates"

    def get_updates(self, offset=0, timeout=30, verify=False):  # 30
        method = "getUpdates"
        params = {"timeout": timeout, "offset": offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()["result"]
        print(result_json)
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

    def get_first_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[0]
        else:
            last_update = None

        return last_update

    def get_chat_history(self):
        pass


token = "1647743462:AAFcjy2b-PhRiYN2z9dkMhTwNgEfD3mPreY"  # Token of your bot
magnito_bot = BotHandler(token)  # Your bot's name


def security_check(update_, offset):

    return True
    secure_ids = [1217535067]
    secure_group_ids = [-518192732, -1001172051071, -568705610]
    if update_["message"]["chat"]["type"] == "private":
        if update_["message"]["from"]["id"] not in secure_ids:
            prijeteca_poruka(offset)
            return False
    else:
        if update_["message"]["chat"]["id"] not in secure_group_ids:
            prijeteca_poruka_grupa(offset)
            return False
    return True


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


DH = DebitHandler()
CC = CCHandler()
LH = LogsHandler()
print("Start")


class BotApi:
    def __init__(self):
        self.new_offset = 0

    def process_updates(self, timeout=30):
        #print("loading updates")
        all_updates = magnito_bot.get_updates(self.new_offset, timeout=timeout)
        #print("updates loaded")
        if len(all_updates) > 0:
            for current_update in all_updates:
                try:
                    
                    current_update_id = current_update["update_id"]
                    self.new_offset = current_update_id + 1

                    if "message" not in current_update:
                        continue

                    if "text" in current_update["message"] and current_update["message"]["text"][0] == "/":
                        update_text = (
                            current_update["message"]["text"][1:]
                            .split("#")[0]
                            .replace("\n", " ")
                            .split(" ")
                    
                        )
                    else:
                        continue

                    update_text = [i for i in update_text if i != ""]

                    print(update_text)
                    chat_id = current_update["message"]["chat"]["id"]
                    
                    if not security_check(current_update, chat_id):
                        continue

                    # dictionery za input
                    # ime razgovora ili osobe
                    if "title" in current_update["message"]["chat"]:
                        title = current_update["message"]["chat"]["title"].replace(
                            " ", "_"
                        )
                    else:
                        title = current_update["message"]["from"]["first_name"]

                    in_dict = {
                        "comm": update_text[0].lower(),
                        "args": update_text[1:],
                        "id": current_update["message"]["chat"]["id"],
                        "title": title,
                    }

                    # komande za sprdačinu
                    custom_commands = CC.load_custom_commands()
                    if in_dict["comm"] in custom_commands:
                        msg_out = custom_commands[in_dict["comm"]]
                        LH.save_input(current_update)

                    # komande za dugove
                    elif in_dict["comm"] in DH.commands:
                        msg_out = DH.commands_API(in_dict)
                        LH.save_input(current_update)

                    # komande za upravljanje sprdačina
                    elif in_dict["comm"] in CC.commands:
                        msg_out = CC.commands_API(in_dict)
                        LH.save_input(current_update)

                    # nije pronađena nijedna komanda
                    else:
                        msg_out = "Unknown command"

                except Exception as e:  #    ERROR
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
            ap.process_updates(timeout = 30)
    except KeyboardInterrupt:
        exit()