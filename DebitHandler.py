import os
import random
import abc

class DataInteractInterface(abc.ABC):
        @abc.abstractmethod
        def load_state(self, chat_id) -> dict:
            pass

        @abc.abstractmethod
        def save_state(self, state, chat_id):
            pass

        @abc.abstractmethod
        def load_groups(self, chat_id) -> dict:
            pass

        @abc.abstractmethod
        def save_groups(self, groups, chat_id):
            pass

        @abc.abstractmethod
        def load_log(self, chat_id) -> tuple:
            pass

        @abc.abstractmethod
        def save_log(self, log, chat_id):
            pass
        
        @abc.abstractmethod
        def get_id_by_name(self, chat_name) -> str:
            pass
        
class DebitHandler:
    def __init__(self, data_instance: DataInteractInterface):
        self.help_path = os.path.join(os.getcwd(), "help.txt")
        self.data_instance = data_instance
        self.commands = {
            "t": self.transaction,
            "td": self.transaction_division,
            "tdex": self.division_transaction_excluding,
            "tg": self.transaction_group,
            "tgex": self.transaction_group_excluding,
            "r": self.get_random_name,
            "s": self.get_state_string,
            "na": self.name_add,
            "nr": self.name_remove,
            "nc": self.name_change,
            "u": self.undo,
            "h": self.get_help_str,
            "help" : self.get_help_str,
            "sum": self.get_state_sum,
            "ga": self.group_add,
            "gr": self.group_delete,
            "gl": self.get_groups_string,
            "st": self.state_transfer,
            "sf": self.state_force,
            "sm": self.state_multiply, #state multiply
            "reset" : self.state_reset,
            "sr" : self.state_reset,
        }
        # 0 - just send succ message, 1 - send succ message and state, 2 - func returns string
        self.succ_respond = {
            "t" : ("Transaction successful",1),
            "td": ("Transaction successful",1),
            "tg": ("Transaction successful",1),
            "tdex": ("Transaction successful",1),
            "tgex": ("Transaction successful",1),
            "u" : ("Undo successful",1),
            "na": ("Name added successfully",1),
            "nr": ("Name removed successfully",1),
            "nc": ("Name changed successfully",1),
            "ga": ("Group added successfully",0),
            "gr": ("Group removed successfully",0),
            "gl": ("", 2),
            "s" : ("", 2),
            "st": ("State transfer successful",1),
            "sf": ("State forced successfully",1),
            "sm": ("State multiplied successfully",1),
            "sr": ("State reset successfully",1),
            "reset" : ("State reset successfully",1),
            "h" : ("", 2),
            "r" : ("", 2),
            "help": ("", 2),
            "sum": ("", 2),
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
        def __init__(self, message = "Duplicate name", name = ""):
            self.message = message
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

    def group_add(self, args, chat_id):
        state = self.data_instance.load_state(chat_id)
        key_word = args[0].upper()
        members = set(map(lambda x: x.capitalize(), args[1:]))

        groups = self.data_instance.load_groups(chat_id)
        if key_word in groups:
            raise DebitHandler.duplicate_name_exception("Group already exists", key_word)
        else:
            for i in members:
                if i not in state:
                    raise DebitHandler.unknown_username_exception(i)

            groups[key_word] = members

        self.data_instance.save_groups(groups, chat_id)
        return True

    def group_delete(self, args, chat_id):
        key_word = args[0].upper()

        groups = self.data_instance.load_groups(chat_id)
        if key_word not in groups:
            raise DebitHandler.unknown_username_exception(key_word)

        del groups[key_word]

        self.data_instance.save_groups(groups, chat_id)
        return True

    def get_groups_string(self, chat_id):
        groups = self.data_instance.load_groups(chat_id)

        end_list = list()
        for i in groups:
            end_list.append("{} - {}".format(i, ", ".join(groups[i])))

        if len(end_list) == 0:
            raise DebitHandler.data_missing_exception()

        return "\n".join(end_list)

    def name_change_groups_fix(self, old_name, new_name, chat_id):
        groups = self.data_instance.load_groups(chat_id)
        key_words = groups.keys()
        for i in key_words:
            for j in range(0, len(groups[i])):
                if old_name == groups[i][j]:
                    groups[i][j] = new_name

        self.data_instance.save_groups(groups, chat_id)
        return True

    def find_dest_chat_id(self, dest_group_name):
        dest_chat_id = self.data_instance.find_chat_id(dest_group_name)
        if dest_chat_id == None:
            raise DebitHandler.unknown_group_exception(dest_group_name)
        return dest_chat_id

    def state_transfer(self, args, chat_id):
        dest_group_name = args[0]
        dest_chat_id = self.find_dest_chat_id(dest_group_name)

        dest_state = self.load_state(dest_chat_id)
        state = self.data_instance.load_state(chat_id)

        members = args[1:]
        transfer_state = dict()
        for i in members:  #  A-ante B-bruno
            i = i.split("-")
            if (i[0].capitalize() not in state):
                raise DebitHandler.unknown_username_exception(i[0])

            elif i[1].capitalize() not in dest_state:
                raise DebitHandler.unknown_username_exception(i[1])

            transfer_state[i[1].capitalize()] = state[i[0].capitalize()]
        # transfer_state = {<dest ime> : <stara vrijednost>}
        # zbraja vrijednosti dvaju stanja

        for i in transfer_state:
            dest_state[i] += transfer_state[i]

        self.data_instance.save_state(dest_state, dest_chat_id)
        self.state_reset(chat_id)
        return True

    def state_reset(self, chat_id):
        data = self.data_instance.load_state(chat_id)
        for i in data:
            data[i] = 0

        self.data_instance.save_state(data, chat_id)
        return True

    def state_force(self, args, chat_id):
        state = dict()
        for i in range(0, len(args), 2):
            if DebitHandler.is_eng_str(args[i]) == False:
                raise DebitHandler.invalid_arguments_exception("Name must contain letters only (Eng)", args[i])

            elif args[i].capitalize() in state:
                raise DebitHandler.duplicate_name_exception("Duplicate name", args[i])
                
            state[args[i].capitalize()] = round(float(args[i + 1]), 2)

        if self.get_state_sum(state) != 0:
            state = DebitHandler.fix_state_inbalance(state)

        self.data_instance.save_state(state, chat_id)
        
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

    def commands_API(self, command_code: str, args: list(), chat_id: int) -> bool:
        if args == list():
            res = self.commands[command_code](chat_id)
        else:
            res = self.commands[command_code](args, chat_id)

        succ_message = self.succ_respond[command_code][0]
        if self.succ_respond[command_code][1] == 0:
            return succ_message

        elif self.succ_respond[command_code][1] == 1:
            return succ_message + "\n---------------------\n" + self.get_state_string(chat_id)

        elif self.succ_respond[command_code][1] == 2:
            return res

    def get_state_string(self, chat_id) -> tuple:
        state = self.data_instance.load_state(chat_id)
        x = list()
        sorted_keys = sorted(state, key=state.get)
        for key in sorted_keys:
            value = state[key]
            if value <= 0:
                s = "{} {}".format(key.strip(), str(round(value, 2)))
                x.append(s)
            elif value > 0:
                s = "{} +{}".format(key.strip(), str(round(value, 2)))
                x.append(s)

        if len(x) == 0:
            raise DebitHandler.data_missing_exception()
        else:
            return "\n".join(x)

    def get_help_str(self, chat_id):
        with open(self.help_path, "r", encoding="utf-8") as f:
            help_str = "".join(f.readlines())
            
        return help_str

    def name_add(self, args, chat_id):
        state = self.data_instance.load_state(chat_id)
        names = set([x.capitalize() for x in args])

        for name in names:
            if not self.is_eng_str(name):
                raise DebitHandler.invalid_arguments_exception("Name must contain letters only", name)

            elif name in state:
                raise DebitHandler.duplicate_name_exception("Duplicate name", name)

            else:
                state[name] = 0

        self.data_instance.save_state(state, chat_id)
        return True

    def name_remove(self, args, chat_id):
        data = self.data_instance.load_state(chat_id)
        names = [x.capitalize() for x in args]

        for name in names:
            if name not in data:
                raise DebitHandler.unknown_username_exception(name)

            elif data[name] != 0:
                raise DebitHandler.forbidden_action_exception("Balance not 0")

            else:
                del data[name]

        self.data_instance.save_state(data, chat_id)
        return True

    def name_change(self, args, chat_id):
        state = self.data_instance.load_state(chat_id)
        if len(args) != 2:
            raise DebitHandler.invalid_command_format_exception("/nc takes 2 arguments", args)

        name, new_name = args[0].capitalize(), args[1].capitalize()

        if not self.is_eng_str(new_name):
            raise DebitHandler.invalid_arguments_exception("Name must contain letters only", new_name)

        elif name not in state:
            raise DebitHandler.unknown_username_exception(name)

        elif new_name in state:
            raise DebitHandler.duplicate_name_exception("Duplicate name",new_name)

        state[new_name] = state.pop(name)
        self.name_change_groups_fix(name, new_name, chat_id)
        self.data_instance.save_state(state, chat_id)

        return True

    def transaction(self, args, chat_id):
        args = DebitHandler.resolvingAlgebraFormations(args)

        state = self.data_instance.load_state(chat_id)

        don = args[0].capitalize()
        recs = list(map(lambda x: x.capitalize(), args[1::2]))
        amounts = list(map(lambda x: x, args[2::2]))


        if don not in state:
            raise DebitHandler.unknown_username_exception(don)

        for i in recs:
            if i not in state:
                raise DebitHandler.unknown_username_exception(i)

        for i in amounts:
            if not self.is_num(i):
                raise DebitHandler.invalid_arguments_exception()

        if len(recs) != len(amounts):
            raise DebitHandler.invalid_command_format_exception()


        amounts = [round(float(x), 2) for x in amounts]

        for i in range(len(recs)):
            state[recs[i]] +=  -1 * amounts[i]

        state[don] += sum(amounts)

        self.data_instance.save_state(state, chat_id)
        return True

    def transaction_division(self, args, chat_id):
        args = DebitHandler.resolvingAlgebraFormations(args)
        state = self.data_instance.load_state(chat_id)

        don = args[0].capitalize()
        recs = list(map(lambda x: x.capitalize(), args[1:-1]))
        money = float(args[-1])

        if don not in state:
            raise DebitHandler.unknown_username_exception(don)

        for i in recs:
            if i not in state:
                raise DebitHandler.unknown_username_exception(i)
        
        money_per_person = round(money / (len(recs) + 1), 2)

        for i in recs:
            state[i.capitalize()] += -1 * money_per_person
        state[don] += money_per_person * len(recs)

        self.data_instance.save_state(state, chat_id)
        return True

    def division_transaction_excluding(self, args, chat_id):
        args = DebitHandler.resolvingAlgebraFormations(args)
        state = self.data_instance.load_state(chat_id)

        don = args[0].capitalize()
        recs = list(map(lambda x: x.capitalize(), args[1:-1]))
        money = float(args[-1])

        if don not in state:
            raise DebitHandler.unknown_username_exception(don)

        for i in recs:
            if i not in state:
                raise DebitHandler.unknown_username_exception(i)
        
        money_per_person = round(money / len(recs), 2)

        for i in recs:
            state[i.capitalize()] += -1 * money_per_person
        state[don] += money_per_person * len(recs)

        self.data_instance.save_state(state, chat_id)
        return True

    def transaction_group(self, args, chat_id):
        args = DebitHandler.resolvingAlgebraFormations(args)
        state = self.data_instance.load_state(chat_id)

        # parsing arguments
        don = args[0].capitalize()
        group_name = args[1].upper()
        money = float(args[2])

        # checking arguments
        if don not in state:
            raise DebitHandler.unknown_username_exception(don)

        groups = self.data_instance.load_groups(chat_id)
        if group_name not in groups:
            raise DebitHandler.unknown_group_exception(group_name)

        members = groups[group_name]

        for i in members:
            if i not in state:
                raise DebitHandler.unknown_username_exception(i)

        # updating state
        money_per_person = round(money / len(members), 2)

        members.remove(don)

        for i in members:
            state[i] += -1 * money_per_person

        state[don] += money_per_person * len(members)

        self.data_instance.save_state(state, chat_id)
        return True
    
    def transaction_group_excluding(self, args, chat_id):
        args = DebitHandler.resolvingAlgebraFormations(args)
        state = self.data_instance.load_state(chat_id)

        # parsing arguments
        don = args[0].capitalize()
        group_name = args[1].upper()
        money = float(args[2])

        # checking arguments
        if don not in state:
            raise DebitHandler.unknown_username_exception(don)

        groups = self.data_instance.load_groups(chat_id)
        if group_name not in groups:
            raise DebitHandler.unknown_group_exception(group_name)

        members = groups[group_name]

        for i in members:
            if i not in state:
                raise DebitHandler.unknown_username_exception(i)

        # updating state
        members.remove(don)

        money_per_person = round(money / len(members), 2)

        for i in members:
            state[i] += -1 * money_per_person

        state[don] += money_per_person * len(members)

        self.data_instance.save_state(state, chat_id)
        return True

    def get_random_name(self, chat_id):
        state = self.data_instance.load_state(chat_id)
        keys = list(state.keys())
        return (random.choice(keys), 0)

    def undo(self, chat_id):
        message = self.data_instance.load_log(chat_id)[2].split(" ")

        if message[0] not in ["/t", "/tg", "/td", "/tgex", "/tdex"]:
            raise DebitHandler.forbidden_action_exception("Only transactions can be undone")

        message = DebitHandler.resolvingAlgebraFormations(message)
        message = DebitHandler.invertNumberSignFromArray(message)

        self.commands[message[0]](message[1:])

        return True

    def get_state_sum(self, state=None, chat_id=None):
        if not state:
            state = self.data_instance.load_state(chat_id)

        L = state.values()
        L = [float(i) for i in L]
        return (round(sum(L), 4), 0)

    def state_multiply(self, args:list, chat_id):
        args = DebitHandler.resolvingAlgebraFormations(args)
        multiplier: float = round(float(args[0]), 2)
        state = self.data_instance.load_state(chat_id)
        name: str
        for name in state.keys():
            state[name] = float(state[name]) * multiplier

        if self.data_instance.save_state(state, chat_id):
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