from DebitHandler import DataInteractInterface
import boto3



class DynamoDBDataClass(DataInteractInterface):
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.states_table = self.dynamodb.Table("States")
        self.groups_table = self.dynamodb.Table("Groups")
        self.logs_table = self.dynamodb.Table("Logs")

    def load_state(self, chat_id) -> dict:
        response = self.states_table.get_item(
            Key={"chat_id": chat_id}
        )
        if "Item" in response:
            return response["Item"]
        else:
            return dict()

    def save_state(self, state, chat_id):
        self.states_table.put_item(
            Item=state,
            Key=chat_id
        )

    def load_groups(self, chat_id) -> dict:
        response = self.groups_table.get_item(
            Key={"chat_id": chat_id}
        )
        if "Item" in response:
            return response["Item"]
        else:
            return dict()

    def save_groups(self, groups, chat_id):
        self.groups_table.put_item(
            Item=groups
        )

    def load_logs(self, chat_id) -> dict:
        response = self.logs_table.get_item(
            Key={"chat_id": chat_id}
        )
        if "Item" in response:
            return response["Item"]
        else:
            return dict()

    def save_logs(self, logs, chat_id):
        self.logs_table.put_item(
            Item=logs
        )

    def load_all_states(self) -> dict:
        response = self.states_table.scan()
        return response["Items"]

    def load_all_groups(self) -> dict:
        response = self.groups_table.scan()
        return response["Items"]

    def load_all_logs(self) -> dict:
        response = self.logs_table.scan()
        return response["Items"]

    def load_all(self) -> dict:
        return {
            "states": self.load_all_states(),
            "groups": self.load_all_groups(),
            "logs": self.load_all_logs()
        }

    def delete_all(self):
        self.states_table.delete()
        self.groups_table.delete()
        self.logs_table.delete()

    def create_all(self):
        self.states_table.create()
        self.groups_table.create()
        self.logs_table.create()

    def delete_state(self, chat_id):
        self.states_table.delete_item(
            Key={"chat_id": chat_id}
        )

    def delete_groups(self, chat_id):
        self.groups_table.delete_item(
            Key={"chat_id": chat_id})