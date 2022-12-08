from LogsHandler import LogsHandler
import os
import random
import glob
import abc



class DebitHandler:
    def __init__(self):
        self.relative_path = os.environ["WRITING_ROOT"]
        self.help_path = os.path.join(os.getcwd(), "help.txt")

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
            "sm": self.state_multiply, #state multiply
            "reset" : self.reset_state,
            "sr" : self.reset_state,
        }

    class unknown_username_exception(Exception):
        def __init__(self, name):
            self.message = "Unknown name"
            self.name = name

        def __str__(self):
            return f"{self.message}: {self.name}"

    class unknown_group_exception(Exception):
        def __init__(self, group):
            self.message = "Unknown group"
            self.group = group

        def __str__(self):
            return f"{self.message}: {self.group}"

    class invalid_arguments_exception(Exception):
        def __init__(self, message, command):
            self.message = message
            self.command = command

        def __str__(self):
            return f"{self.message}: {self.command}"

    class duplicate_name_exception(Exception):
        def __init__(self, name = ""):
            self.message = "Duplicate name"
            self.name = name

        def __str__(self):
            return f"{self.message}: {self.name}"

    class data_missing_exception(Exception):
        def __init__(self, message = "Empty :("):
            self.message = message

        def __str__(self):
            return f"{self.message}"
    
    class invalid_command_format_exception(Exception):
        def __init__(self, message = "Invalid command", command = "h"):
            self.message = message
            self.command = command

        def __str__(self):
            return f"{self.message}"
    
    class forbidden_action_exception(Exception):
        def __init__(self, message = "Forbidden request"):
            self.message = message

        def __str__(self):
            return f"{self.message}"
    
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

    def group_create(self, args):
        state = self.load_data()
        key_word = args[0].upper()
        members = list(map(lambda x: x.capitalize(), args[1:]))
        groups = self.load_groups()
        if key_word in groups:
            raise DebitHandler.duplicate_name_exception("Group already exists", key_word)
        else:
            for i in members:
                if i not in state:
                    raise DebitHandler.unknown_username_exception(i)

            groups[key_word] = members

        self.save_groups(groups)
        return ("Group created", 0)

    def save_groups(self, groups):
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

        groups = self.load_groups()
        if key_word not in groups:
            raise DebitHandler.unknown_username_exception(key_word)

        del groups[key_word]

        self.save_groups(groups)
        return ("Group deleted", 0)

    def groups_print(self):
        groups = self.load_groups()

        end_list = list()
        for i in groups:
            end_list.append("{} - {}".format(i, ", ".join(groups[i])))

        if len(end_list) == 0:
            raise DebitHandler.data_missing_exception()

        return ("\n".join(end_list), 0)

    def load_groups(self):
        try:
            with open(self.groups_path, "r") as f:
                text = f.readlines()

        except:  # ako ne postoji, napravi file i vrati prazni dict
            with open(self.groups_path, "a") as f:
                pass
            return dict()

        groups = dict()
        for i in text:
            x = i.strip().split("-")
            groups[x[0]] = x[1].split(" ")
        return groups

    def name_change_groups_fix(self, old_name, new_name):
        groups = self.load_groups()
        key_words = groups.keys()
        for i in key_words:
            for j in range(0, len(groups[i])):
                if old_name == groups[i][j]:
                    groups[i][j] = new_name

        self.save_groups(groups)
        return True

    def state_transfer(self, args):
        dest_group_name = args[0]
        dest_group_path = self.find_dest_group_path(dest_group_name)

        dest_group_state = self.load_data(dest_group_path)
        state = self.load_data()

        members = args[1:]
        transfer_state = dict()
        for i in members:  #  A-ante B-bruno
            i = i.split("-")
            if (i[0].capitalize() not in state):
                raise DebitHandler.unknown_username_exception(i[0])

            elif i[1].capitalize() not in dest_group_state:
                raise DebitHandler.unknown_username_exception(i[1])

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
            raise DebitHandler.duplicate_name_exception("Multiple groups with same name", name)

        elif len(dirname_) == 0:
            raise DebitHandler.unknown_group_exception(name)

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
                raise DebitHandler.invalid_arguments_exception("Name must contain letters only (Eng)", args[i])

            elif args[i].capitalize() in state:
                raise DebitHandler.duplicate_name_exception("Duplicate name", args[i])
                
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
            raise DebitHandler.data_missing_exception()
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
                raise DebitHandler.invalid_arguments_exception("Name must contain letters only (Eng)", name)

            elif name in data:
                raise DebitHandler.duplicate_name_exception("Duplicate name", name)

            else:
                data[name] = 0

        self.save_state(data)
        return ("Name added", 1)

    def remove_name(self, args):
        data = self.load_data()
        name = args[0].capitalize()
        if len(args) != 1:
            raise DebitHandler.invalid_command_format_exception("/rm takes 1 argument", name)

        elif name not in data:
            raise DebitHandler.unknown_username_exception("Name not on the list", name)

        elif data[name] != 0:
            raise DebitHandler.forbidden_action_exception("Balance not 0")

        else:
            del data[name]

        self.save_state(data)
        return ("Name removed", 1)

    def change_name(self, args):
        data = self.load_data()
        if len(args) != 2:
            raise DebitHandler.invalid_command_format_exception("/nc takes 2 arguments", args)

        name, new_name = args[0].capitalize(), args[1].capitalize()

        if not self.is_eng_str(new_name):
            raise DebitHandler.invalid_arguments_exception("Name must contain letters only (Eng)", new_name)

        elif name not in data:
            raise DebitHandler.unknown_username_exception(name)

        elif new_name in data:
            raise DebitHandler.duplicate_name_exception(new_name)

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
            raise DebitHandler.unknown_username_exception(don)

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
            raise DebitHandler.unknown_username_exception(don)

        for i in recs:
            if i.capitalize() not in data:
                raise DebitHandler.unknown_username_exception(i)

        for i in amounts:
            if not self.is_num(i):
                raise DebitHandler.invalid_arguments_exception()

        if len(recs) != len(amounts):
            raise DebitHandler.invalid_command_format_exception()

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
            raise DebitHandler.unknown_username_exception(don)

        groups = self.load_groups()
        if group_name not in groups:
            raise DebitHandler.unknown_group_exception(group_name)

        rec = groups[group_name]

        if don not in rec:
            raise DebitHandler.unknown_username_exception(don)

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
            raise DebitHandler.forbidden_action_exception("Only transactions can be undone")

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

    def state_multiply(self, args:list):
        args = DebitHandler.resolvingAlgebraFormations(args)
        multiplier: float = round(float(args[0]), 2)
        state = self.load_data()
        name: str
        for name in state.keys():
            state[name] = float(state[name]) * multiplier

        if self.save_state(state):
            return ("State multiplied", 1)
        else:
            raise DebitHandler.forbidden_action_exception("Sum is not 0")

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