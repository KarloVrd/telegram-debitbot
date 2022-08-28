import os
from DebitHandler import DebitHandler
from sys import platform


class CCHandler:
    def __init__(self):
        if platform == "win32":
            self.relative_path = os.path.dirname(__file__)
        else:
            self.relative_path = "/storage/emulated/0/Moji programi/DebitBot_v6"
            
        self.custom_commands_path = os.path.join(self.relative_path, "custom_comm.txt")
        self.custom_commands = self.load_custom_commands()

        self.commands = {
            "cl": self.commands_list_print_format,
            "cc": self.add_custom_comm,
            "cr": self.remove_custom_comm,
        }

    def commands_API(self, in_dict):
        if in_dict["args"] == list():
            res = self.commands[in_dict["comm"]]()
        else:
            res = self.commands[in_dict["comm"]](in_dict["args"])

        return res

    def load_custom_commands(self):
        try:
            f = open(self.custom_commands_path, "r", encoding="utf-8")
            L = f.readlines()
            f.close()
            dict1 = dict()
            for i in L:
                i = i.strip().split("-")
                dict1[i[0]] = i[1]

        except FileNotFoundError:
            f = open(self.custom_commands_path, "w")
            f.close()
            dict1 = dict()

        return dict1

    def add_custom_comm(self, args):
        ccommands = self.load_custom_commands()
        key = args[0].lower()
        value = " ".join(args[1:])

        if key in ccommands:
            return ("Command already exists", 0)

        if any(
            ((not letter.isalpha() and letter != "_") or letter in "šđžčć")
            for letter in key
        ):
            return ("Key must contain letters only (Eng)", 0)

        ccommands[key] = value
        self.save_commands(ccommands)
        return ("Command added", 0)

    def remove_custom_comm(self, args):
        ccommands = self.load_custom_commands()
        key = args[0]
        if key not in ccommands:
            return ("Command nonexisting", 0)

        del ccommands[key]

        self.save_commands(ccommands)
        return ("Command removed", 0)

    def save_commands(self, ccommands):
        f = open(self.custom_commands_path, "w", encoding="utf-8")
        list1 = list()
        for i in ccommands:
            list1.append("{}-{}".format(i, ccommands[i]))
        f.write("\n".join(list1))
        f.close()

    def commands_list_print_format(self):
        ccommands = self.load_custom_commands()
        msg_out_L = list()
        for i in ccommands.keys():
            msg_out_L.append("/" + i)
        return ("\n".join(msg_out_L), 0)

    def respond(self, key):
        if key not in self.custom_commands:
            return "Unknown command"
        else:
            return self.custom_commands[key]
