import os
import time
from sys import platform
import CONFIG


class LogsHandler:
    if platform == "win32":
        relative_path = os.path.dirname(__file__)
    else:
        relative_path = CONFIG.relativePath

    @classmethod
    def save_input(cls, current_update):
        date = time.localtime(current_update["message"]["date"])
        strdate = time.strftime("%d/%m/%Y_%H:%M:%S", date)

        if "username" in current_update["message"]["from"]:
            name = "@" + current_update["message"]["from"]["username"]

        elif "last_name" not in current_update["message"]["from"]:
            name = "{}".format(current_update["message"]["from"]["first_name"])

        else:
            name = "{}_{}".format(
                current_update["message"]["from"]["first_name"],
                current_update["message"]["from"]["last_name"],
            )

        name += "_" + str(current_update["message"]["from"]["id"])

        text = current_update["message"]["text"].split(" ")
        text = "_".join(text)

        out = "[{}] [{}] {}\n".format(strdate, name, text)

        logs_path = os.path.join(
            cls.relative_path,
            "Logs",
            str(current_update["message"]["chat"]["id"]) + ".txt",
        )
        f = open(logs_path, "a")
        f.write(out)
        f.close()

    @classmethod  # trenutno ne radi nista
    def save_output(cls, msg):
        date = time.localtime()
        strdate = time.strftime("%Y/%m/%d %H:%M:%S", date)

        out = "[{}] [BotReply]: {}\n".format(strdate, msg)

        f = open(cls.path, "a")
        f.write(out)
        f.close()

    @classmethod
    def load_logs(cls, path):
        try:
            f = open(path, "r")
            logs = f.readlines()
            logs = [i.strip() for i in logs]

        except FileNotFoundError:
            f = open(path, "w")
            logs = list()

        f.close()
        return logs

    @classmethod
    def get_undo_last_command(cls, path):
        logs = cls.load_logs(path)
        last_log = logs[len(logs) - 1].split(" ")

        command = last_log[2].split("_")
        if command[0] in ["t", "td", "tg"] and "UNDONE" not in last_log:
            logs[len(logs) - 1] += " UNDONE"
            f = open(path, "w")
            f.write("\n".join(logs) + "\n")
            f.close()

            return command
        
        else:
            return None

    @classmethod
    def clear_logs(cls):
        f = open(cls.path, "w")
        f.close()
        return "Cleared"


# LogsHandler.clear_logs()
