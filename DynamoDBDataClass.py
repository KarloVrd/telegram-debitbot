from DebitHandler import DataInteractInterface
import boto3
import os
import datetime
from decimal import Decimal
import json
talbe_name = os.environ["DYNAMODB_TABLE_NAME"]

class DynamoDBDataClass(DataInteractInterface):
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(talbe_name)

    def load_state(self, chat_id: int) -> dict:
        response = self.table.get_item(
            Key={"chat_id": chat_id},
            AttributesToGet = ["state"]
        )
        if "Item" in response and "state" in response["Item"]:
            low_level_data = response["Item"]["state"]
            python_data = {k: float(v) for k,v in low_level_data.items()}
            return python_data
        else:
            return dict()

    def save_state(self, state, chat_id: int):
        # convert float to Decimal
        state = json.loads(json.dumps(state), parse_float=Decimal)

        self.table.update_item(
            Key={"chat_id": chat_id},
            AttributeUpdates={
            'state': {
                'Value': state,
                'Action': 'PUT'
            }
    }
        )

    def load_groups(self, chat_id: int) -> dict:
        response = self.table.get_item(
            Key={"chat_id": chat_id},
            AttributesToGet = ["groups"]
        )

        if "Item" in response and "groups" in response["Item"]:
            return response["Item"]["groups"]
        else:
            return dict()

    def save_groups(self, groups, chat_id: int):
        self.table.update_item(
            Key={"chat_id": chat_id},
            AttributeUpdates={
                'groups': {
                    'Value': groups,
                    'Action': 'PUT'
                }
            }
        )
    # get the last log in the list
    def load_log(self, chat_id: int, reverse_index: int) -> dict:
        response = self.table.get_item(
            Key={"chat_id": chat_id},
            ProjectionExpression = "logs[0]"
        )
        print(response)
        index = reverse_index
        if "Item" in response and "logs" in response["Item"]:

            return response["Item"]["logs"][index]
        else:
            return dict()
        
    # append log to the end of the list in dynamodb
    def save_log(self, chat_id: int, sender_id: int, command: str):
        # convert args to string
        sender_id = int(sender_id)
        chat_id = int(chat_id)
        dateTimeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = {
            "date_time": dateTimeStr,
            "sender_id": sender_id,
            "command": command
        }
        try:
            self.table.update_item(
                Key={"chat_id": chat_id},
                UpdateExpression="SET logs = list_append(:i, logs)",
                ExpressionAttributeValues={
                    ':i': [item]
                }
            )
        except Exception as e:
            # create logs list
            self.table.update_item(
                Key={"chat_id": chat_id},
                AttributeUpdates={
                    'logs': {
                        'Value': [item],
                        'Action': 'PUT'
                    }
                }
            )

    def remove_log(self, chat_id: int, reverse_index: int):
        index = reverse_index
        self.table.update_item(
            Key={"chat_id": chat_id},
            UpdateExpression="REMOVE logs[{}]".format(index)
        )
        
    def get_id_by_name(self, chat_name) -> str:
        return 0

    def convert_decimal_to_float(self, low_level_data):
        for k in low_level_data:
            if isinstance(low_level_data[k], dict):
                self.convert_decimal_to_float(low_level_data[k])
            elif isinstance(low_level_data[k], Decimal):
                low_level_data[k] = float(low_level_data[k])
            elif isinstance(low_level_data[k], list):
                self.convert_decimal_to_float(low_level_data[k])
        
    def covert_float_to_decimal(self, python_data):
        return json.loads(json.dumps(python_data), parse_float=Decimal)

if __name__ == "__main__":
    data = DynamoDBDataClass()
    print(data.load_log(1217535067,0))