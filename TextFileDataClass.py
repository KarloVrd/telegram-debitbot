import os, time
from DebitHandler import DebitHandler
import glob

from AbstractDatabase import AbstractDatabase

class TextFileDataClass(AbstractDatabase):
    def __init__(self):
        self.states_path = os.path.join(os.environ["WRITING_ROOT"], "States")
        self.groups_path = os.path.join(os.environ["WRITING_ROOT"], "Groups")
        self.logs_path = os.path.join(os.environ["WRITING_ROOT"], "Logs")

    def load_state(self, chat_id) -> dict:
        state = dict()  
        chat_id = str(chat_id)
        # open any file with the chat_id upfront
        path_list = glob.glob(os.path.join(self.states_path, chat_id + "*.txt"))
        if len(path_list) == 1:

            # old version were using utf-8
            try:
                with open(path_list[0], "r", encoding="utf-16") as f:
                    data = f.readlines()
            except UnicodeError:
                with open(path_list[0], "r", encoding="utf-8") as f:
                    data = f.readlines()

            for i in data:
                i = i.split(" ")
                state[i[0]] = float(i[1])

        elif len(path_list) == 0:
            # create file
            chat_state_path = os.path.join(self.states_path, chat_id + ".txt")
            with open(chat_state_path, "w") as f:
                pass
                
        else:
            raise DebitHandler.duplicate_name_exception("More than one file with the same chat id")

        return state

    def save_state(self, state, chat_id):
        chat_id = str(chat_id)
        chat_state_path = glob.glob(os.path.join(self.states_path, chat_id + "*.txt"))[0]

        with open(chat_state_path, "w", encoding="utf-16") as f:
            for key in state.keys():
                f.write("{} {}\n".format(key, state[key]))

    def load_groups(self, chat_id) -> dict:
        chat_id = str(chat_id)
        groups = dict()

        # open any file with the chat_id infront
        path_list = glob.glob(os.path.join(self.groups_path, chat_id + "*.txt"))
        if len(path_list) == 1:
            path = path_list[0]
            
            # old version were using utf-8
            try:     
                with open(path, "r", encoding="utf-16") as f:
                    text = f.readlines()
            except UnicodeError:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.readlines()

            for i in text:
                x = i.strip().split("-")
                groups[x[0]] = x[1].split(" ")

        elif len(path_list) == 0:
            chat_groups_path = os.path.join(self.groups_path, chat_id + ".txt")

            # create file
            with open(chat_groups_path, "w") as f:
                pass

        else:
            raise DebitHandler.duplicate_name_exception("More than one file with the same chat id")

        return groups

    def save_groups(self, groups, chat_id):
        chat_id = str(chat_id)
        chat_groups_path = glob.glob(os.path.join(self.groups_path, chat_id + "*.txt"))[0]

        with open(chat_groups_path, "w", encoding="utf-16") as f:
            for key in groups.keys():
                f.write("{}-{}\n".format(key, " ".join(groups[key])))

    def load_log(self, chat_id, index_reverse = 0) -> tuple:
        chat_id = str(chat_id)
        index = -1 - index_reverse
        path = os.path.join(self.logs_path, chat_id + ".txt")

        with open(path, "r", encoding="utf-16") as f:
            log_list = f.readlines()[index].strip().split(" ")

        return log_list

    def save_log(self, chat_id, sender_id, message):
        chat_id = str(chat_id)
        sender_id = str(sender_id)

        date = time.localtime()
        strdate = time.strftime("%Y/%m/%d_%H:%M:%S", date)
        
        log = "{}|{}|{}".format(strdate, sender_id, message)

        path = os.path.join(self.logs_path, chat_id + ".txt")

        with open(path, "a", encoding="utf-16") as f:
            f.write(log + "\n")

    def get_id_by_name(self, chat_name):
        path = os.path.join(self.states_path, "*" + chat_name + ".txt")
        num_of_files = glob.glob(path)

        if len(num_of_files) == 0:
            return None
        elif len(num_of_files) == 1:
            file_name = os.path.basename(num_of_files[0])
            return file_name.split("_")[0]
        else:
            raise DebitHandler.duplicate_name_exception("There are multiple groups with the same name", chat_name)

    def load_logs(cls, path):
        try:
            with open(path, "r", encoding="utf-16") as f:
                logs = f.readlines()
                logs = [i.strip() for i in logs]

        except FileNotFoundError:
            with open(path, "w") as f:
                pass    
            logs = list()

        return logs

# test get_id_by_name
if __name__ == "__main__":
    t = TextFileDataClass()
    print(t.save_log("-568234974", "3", "/t vrljo tomas 40 miha 30"))
    print(t.get_id_by_name("Ciovo"))