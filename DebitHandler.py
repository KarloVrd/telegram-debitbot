from LogsHandler import LogsHandler
import os
import random
import glob
from sys import platform

class DebitHandler:
    def __init__(self):
        self.relative_path = os.getcwd()
        self.help_path = os.path.join(self.relative_path, "help.txt")

        self.commands = {
            "t": self.transaction,
            "td": self.division_transaction,
            "tg": self.group_transaction,
            "r": self.random_name,
            "s": self.data_print_format,
            "na": self.add_name,
            "nr": self.remove_name,
            "nc": self.change_name,
            "u": self.undo,
            "h": self.load_help_str,
            "help" : self.load_help_str,
            "sum": self.sum,
            "gc": self.group_create,
            "gr": self.group_delete,
            "gl": self.groups_print,
            "st": self.state_transfer,
            "sf": self.force_state,
            "reset" : self.reset_state,
            "currencyconvert": self.currencyConvert,
        }

    @staticmethod
    def is_num(x):
        try:
            float(x)
            return True

        except ValueError:
            return False

    @staticmethod
    def is_eng_str(str1):
        if all(letter.isalpha() for letter in str1):
            return True
        else:
            return False

    @staticmethod
    def contains_mixed_letters_and_non_letters(string):
        return any(letter.isalpha() for letter in string) and any(
            not letter.isalpha() for letter in string
        )
    
    @staticmethod
    def resolvingAlgebraFormations(array: list) -> list:
            i = 0
            isLastNum: bool = False

            while (i < len(array)):
                if DebitHandler.is_eng_str(array[i]) == False:
                    if isLastNum:
                        array[i - 1] = array[i - 1] + array[i]
                        array.pop(i)
                    else:
                        i += 1
                    isLastNum = True
                else:
                    if isLastNum == True:
                        array[i-1] = eval(array[i-1])
                    isLastNum = False
                    i += 1

            if isLastNum == True:
                array[-1] = eval(array[-1])

            return array
        # except:
        #     return NULL

    def group_create(self, args):
        state = self.load_data()
        key_word = args[0].upper()
        members = list(map(lambda x: x.capitalize(), args[1:]))

        groups = self.load_groups()
        if key_word in groups:
            return ("Group already exists", 0)
        else:
            memebers = list(set(members))
            for i in members:
                if i not in state:
                    return ("Member name nonexisting", 0)

            groups[key_word] = members

        self.save_groups(groups)
        return ("Group created", 0)

    def save_groups(self, groups):
        if DebitHandler.sum(groups) != 0:
            return False

        groups_list = list()
        for i in groups:
            groups_list.append(i + "-" + " ".join(groups[i]))
        f = open(self.groups_path, "w")
        end_str = "\n".join(groups_list)
        f.write(end_str)
        f.close()
        return True

    def group_delete(self, args):
        key_word = args[0].upper()
        members = list(map(lambda x: x.capitalize(), args[1:]))

        groups = self.load_groups()
        if key_word not in groups:
            return ("Group nonexistent", 0)
        else:
            del groups[key_word]

        self.save_groups(groups)
        return ("Group deleted", 0)

    def groups_print(self):
        groups = self.load_groups()

        end_list = list()
        for i in groups:
            end_list.append("{} - {}".format(i, ", ".join(groups[i])))

        return ("\n".join(end_list), 0)

    def load_groups(self):
        try:
            f = open(self.groups_path, "r")

        except:  # ako ne postoji, napravi file i vrati prazni dict
            f = open(self.groups_path, "a")
            return dict()

        text = f.readlines()
        f.close()
        groups = dict()
        for i in text:
            x = i.strip().split("-")
            groups[x[0]] = x[1].split(" ")
        return groups

    def groups_check(self, args):
        don = args[0].capitalize()
        key_word = args[1].upper()
        groups = self.load_groups()

        if key_word not in groups:
            return "Group nonexisting"
        else:
            if don not in groups[key_word]:
                return "Name not in group"
            else:
                members = groups[key_word]

        members.remove(args[0].capitalize())
        args.remove(args[1])
        for i in members:
            args.insert(-1, i)
        return args

    def name_change_groups_fix(self, old_name, new_name):
        groups = self.load_groups()
        key_words = groups.keys()
        for i in key_words:
            for j in range(0, len(groups[i])):
                if old_name == groups[i][j]:
                    groups[i][j] = new_name

        self.save_groups(groups)
        return True

    def inverse_group_check(self, command):
        key_word = command[2]
        groups = self.load_groups()
        don = command[1].capitalize()
        if key_word in groups:

            members = groups[key_word]
            members.remove(don)
            command.remove(command[2])
            for i in members:
                command.insert(2, i)
            return command
        else:
            return 0

    def state_transfer(self, args):
        # return (0,0)
        dest_group_name = args[0]
        valid, res = self.find_dest_group_path(dest_group_name)
        if valid is True:
            dest_group_path = res
        else:
            return (res, 0)

        dest_group_state = self.load_data(dest_group_path)
        state = self.load_data()

        members = args[1:]
        transfer_state = dict()
        for i in members:  #  A-ante B-bruno
            i = i.split("-")
            if (
                i[0].capitalize() not in state
                or i[1].capitalize() not in dest_group_state
            ):
                return ("Name nonexisting", 0)

            transfer_state[i[1].capitalize()] = state[i[0].capitalize()]
        # transfer_state = {<dest ime> : <stara vrijednost>}
        # zbraja vrijednosti dvaju stanja

        for i in transfer_state:
            dest_group_state[i] += transfer_state[i]

        self.save_state(dest_group_state, dest_group_path)
        self.reset_state()
        return ("Group transfered", 0)

    def find_dest_group_path(self, name):
        dirname_ = glob.glob(
            os.path.join(self.relative_path, "States", "*_" + name + ".txt")
        )
        path = os.path.join(self.relative_path, dirname_[0])

        if len(dirname_) > 1:
            return False, "More groups under same name"

        elif len(dirname_) == 0:
            return False, "Group name nonexisting"

        else:
            return True, path

    def reset_state(self):
        data = self.load_data()
        for i in data:
            data[i] = 0

        self.save_state(data)
        return ("State reset", 1)

    def force_state(self, args):
        state = dict()
        for i in range(0, len(args), 2):
            if DebitHandler.is_eng_str(args[i]) == False:
                return ("Name must contain letters only (Eng)", 0)

            elif args[i].capitalize() in state:
                return ("Name repeated", 0)
                
            state[args[i].capitalize()] = round(float(args[i + 1]), 2)

        inbalance_fixed = False
        if self.sum(state) != 0:
            state = DebitHandler.fix_state_inbalance(state)
            inbalance_fixed = True

        if self.save_state(state):
            if inbalance_fixed:
                return ("State forced, inbalance fixed", 1)
            else:
                return ("Force state complete", 1)
        else:
            return ("Error; sum not 0", 0)
        
    # state is better name for group state
    @staticmethod
    def fix_state_inbalance(state: dict) -> dict:
        difference = sum(list(state.values()))
        remainder = (100 * difference % len(state)) / 100
        for i in state:
            state[i] -= (100 * difference // len(state)) / 100

        for i in range(0, int(remainder * 100)):
            state[list(state.keys())[i]] -= 0.01
    
        return state

    def commands_API(self, in_dict):
        # return (0,0)
        self.id = in_dict["id"]
        self.data_path = os.path.join(
            self.relative_path,
            "States",
            str(in_dict["id"]) + "_" + str(in_dict["title"]) + ".txt",
        )
        self.groups_path = os.path.join(
            self.relative_path, "Groups", str(self.id) + ".txt"
        )

        if in_dict["args"] == list():
            res = self.commands[in_dict["comm"]]()
        else:
            res = self.commands[in_dict["comm"]](in_dict["args"])

        # printa listu dugova ako treba
        if res[1]:
            msg_out = "{}:\n------------------\n{}".format(
                res[0], self.data_print_format()[0]
            )

        else:  # ne printa listu
            msg_out = res[0]

        return msg_out

    def load_data(self, path=False) -> dict:
        if not path:
            path = self.data_path
        data = dict()
        try:
            f = open(path, "r")  # , encoding='utf-8')
            data = f.readlines()
            f.close()
            dict1 = dict()
            for i in data:
                i = i.split(" ")
                dict1[i[0]] = float(i[1])

        except FileNotFoundError:
            dirname_ = glob.glob(os.path.join(path.split("_")[0] + "*.txt"))

            # promijenjeno je ime grupe, bot treba promijeniti ime u zapisima
            if len(dirname_) == 1:
                old_data_path = os.path.join(self.relative_path, dirname_[0])
                os.rename(old_data_path, path)

                f = open(path, "r")  # , encoding='utf-8')
                data = f.readlines()
                f.close()
                dict1 = dict()
                for i in data:
                    i = i.split(" ")
                    dict1[i[0]] = float(i[1])

            # grupa nije postojala
            else:
                f = open(self.data_path, "w")
                f.close()
                dict1 = dict()

        return dict1

    def save_state(self, data, path=False):
        if not path:
            path = self.data_path

        x = list()
        for key in data.keys():

            name = key.strip().capitalize()
            value = str(round(float(data[key]), 2))

            s = "{} {}".format(name, value)
            x.append(s)
        text = "\n".join(x)

        f = open(path, "w")
        f.write(text)
        f.close()
        return True

    def data_print_format(self):
        data = self.load_data()
        x = list()
        sorted_keys = sorted(data, key=data.get)
        for key in sorted_keys:
            value = data[key]
            if value <= 0:
                s = "{} {}".format(key.strip(), str(round(value, 2)))
                x.append(s)
            elif value > 0:
                s = "{} +{}".format(key.strip(), str(round(value, 2)))
                x.append(s)

        if x == list():
            return ("Empty :(", 0)
        else:
            return ("\n".join(x), 0)

    def updata_value(self, name, money):
        data = self.load_data()
        data[name] += money
        self.save_state(data)

    def load_help_str(self):
        f = open(self.help_path, "r", encoding="utf-8")
        help_str = "".join(f.readlines())
        f.close()
        return (help_str, 0)

    def add_name(self, args):
        data = self.load_data()
        for name in args:
            name = name.capitalize()
            if not self.is_eng_str(name):
                return ("Name must contain letters only (Eng)", 0)

            elif name in data:
                return ("Name already taken", 0)

            else:
                data[name] = 0

        self.save_state(data)
        return ("Name added", 1)

    def remove_name(self, args):
        data = self.load_data()
        name = args[0].capitalize()
        if len(args) != 1:
            return ("Invalid command", 0)

        elif name not in data:
            return ("Name not on the list", 0)

        elif data[name] != 0:
            return ("Balance not 0", 0)

        else:
            del data[name]

        self.save_state(data)
        return ("Name removed", 1)

    def change_name(self, args):
        data = self.load_data()
        if len(args) != 2:
            return ("Invalid command", 0)
        name, new_name = args[0].capitalize(), args[1].capitalize()

        if not self.is_eng_str(new_name):
            return ("Name must contain letters only (Eng)", 0)

        elif name not in data:
            return ("Name not on the list", 0)

        elif new_name in data:
            return ("Name already taken", 0)

        data[new_name] = data.pop(name)
        self.save_state(data)
        self.name_change_groups_fix(name, new_name)

        return ("Name changed", 1)

    def division_transaction(self, args):
        args = DebitHandler.resolvingAlgebraFormations(args)
        data = self.load_data()

        don = args[0].capitalize()
        rec = args[1:-1]
        money = float(args[-1])

        if don not in data:
            return ("Name not on the list", 0)

        # Provjera je li komanda namijenjena za grupu
        if len(rec) == 1 and rec[0] == rec[0].upper():
            check = self.groups_check(args)

            if type(check) == str:
                return (check, 0)
            else:
                args = check
                rec = args[1:-1]

        else:
            for i in rec:
                if i.capitalize() not in data:
                    return ("Name not on the list", 0)

        money_per_person = round(money / (len(rec) + 1), 2)

        for i in rec:
            self.updata_value(i.capitalize(), -1 * money_per_person)
        self.updata_value(don, money_per_person * len(rec))
        return ("Transaction complete", 1)

    def transaction(self, args):
        args = DebitHandler.resolvingAlgebraFormations(args)

        data = self.load_data()
        don = args[0].capitalize()
        recs = list(map(lambda x: x.capitalize(), args[1::2]))
        amounts = list(map(lambda x: x, args[2::2]))
        if don.capitalize() not in data:
            return ("Name not on the list", 0)

        for i in recs:
            if i.capitalize() not in data:
                return ("Name not on the list", 0)

        for i in amounts:
            if not self.is_num(i):
                return ("Invalid command", 0)

        if len(recs) != len(amounts):
            return ("Invalid command", 0)

        amounts = [round(float(x), 2) for x in amounts]

        for i in range(len(recs)):
            self.updata_value(recs[i], -1 * amounts[i])

        self.updata_value(don, sum(amounts))

        return ("Transaction complete", 1)

    def group_transaction(self, args):
        args = DebitHandler.resolvingAlgebraFormations(args)
        state = self.load_data()

        don = args[0].capitalize()
        group_name = args[1].upper()
        money = float(args[2])

        if don not in state:
            return ("Name not on list", 0)

        groups = self.load_groups()
        if group_name not in groups:
            return ("Group nonexisting", 0)
        else:
            rec = groups[group_name]

            if don not in rec:
                return ("Name not in group", 0)

            rec.remove(don)

        money_per_person = round(money / (len(rec) + 1),2)

        for i in rec:
            self.updata_value(i.capitalize(), -1 * money_per_person)
        self.updata_value(don, money_per_person * len(rec))
        return ("Transaction complete", 1)

    def random_name(self):
        data = self.load_data()
        keys = list(data.keys())
        return (random.choice(keys), 0)

    def undo(self):
        path = os.path.join(self.relative_path, "Logs", str(self.id) + ".txt")
        command = LogsHandler.get_undo_last_command(path)
        if command == None:
            return ("Only transactions can be undone", 0)

        command = DebitHandler.resolvingAlgebraFormations(command)

        command = DebitHandler.invertNumberSignFromArray(command)

        self.commands[command[0]](command[1:])

        return ("Undone", 1)

    def sum(self, state=False):
        if not state:
            state = self.load_data()
        L = state.values()
        L = [float(i) for i in L]
        return (round(sum(L), 4), 0)

    def currencyConvert(self, args:list):
        args = DebitHandler.resolvingAlgebraFormations(args)
        multiplier: float = round(float(args[0]), 2)
        state = self.load_data()
        name: str
        for name in state.keys():
            state[name] = float(state[name]) * multiplier

        if self.save_state(state):
            return ("Currency converted",1)
        else:
            return ("Error; sum not 0", 0)

    @staticmethod
    def invertNumberSignFromArray(args:list):
        for i in args:
            if DebitHandler.is_num(i):
                args[args.index(i)] = str(float(i) * -1)

        return args
if __name__ == '__main__':
    array = ['/Transaction','3', '+','5', '-','4','-4', '/Karlo', 'Jura', "(4+90)",'/3','Gjuto',"-3"]
    array = DebitHandler.resolvingAlgebraFormations(array)
    print("Array:",array)