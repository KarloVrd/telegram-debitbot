import abc

class AbstractDatabase(abc.ABC):
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
    def load_log(self, chat_id, reverse_index) -> tuple:
        pass

    @abc.abstractmethod
    def save_log(self, message:str, sender_id, chat_id):
        pass
    
    @abc.abstractmethod
    def get_id_by_name(self, chat_name) -> str:
        pass

    @abc.abstractmethod
    def load_log_after_time(self, chat_id, time, reverse_index, ) -> list:
        pass