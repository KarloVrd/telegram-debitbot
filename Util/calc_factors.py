from AbstractDatabase import AbstractDatabase

from datetime import datetime, timedelta

def calc_players_k(database: AbstractDatabase, chat_id: int, time: datetime) -> dict:
    """
    Function calculates k value for each player in the chat.
    K value is calculated by the amount of games played by the player in last 60 days.
    Function is continuous and monotonic, meaning that the more games a player played, the higher k value they get.
    0 games -> 32
    1 game -> 27
    2 games -> 23
    3 games -> 20
    4 games -> 18
    5 games -> 16
    """
    # Load log from database
    log = database.load_log_after_time(chat_id, time - timedelta(days=60))
    players_k = {}
    for game in log:
        players = game['players']
        for player in players:
            if player not in players_k:
                players_k[player] = 0
            players_k[player] += 1


def calc_l_factor(num_of_players: int) -> float:
    """
    Function calculates l factor based on number of players in the game.
    L factor is higher with more players.

    2 players -> 1.0
    3 players -> 1.2
    4 players -> 1.4
    5 players -> 1.6
    ...
    """
    if num_of_players < 2:
        return 0.0
    return 1.0 + (num_of_players - 2) * 0.2
