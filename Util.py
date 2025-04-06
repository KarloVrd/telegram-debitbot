
def calculate_elo_diff(player_elo: int, opponent_elo: int, actual_score: float = 1, k: int = 32) -> int:
    '''
    Function calculates elo difference between two players
    k is a constant that determines how much elo will be gained or lost
    '''
    expected_score = 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
    return int(k * (actual_score - expected_score))

def calc_order_elo(players_dict: dict, winning_order: list):
    '''
    Function calculates new elo ratings for every player
    Due to nature of the game, players are getting eliminated until the last one
    For each player we calculate (excluding first and last player):
    - average elo of all players that were eliminated before him
    - average elo of all players that stayed in the game after him
    - k based on number of players in each list (adds up to 32)
    - elo difference for both lists and add them to the player's elo
    
    First and last player have different calculations:
    - winner gains elo based on average of all other players (k = 32)
    - first eliminated loses elo based on average of all other players (k = 32)

    '''
    new_elo = players_dict.copy()
    num_of_opponents = len(winning_order) - 1

    for i, player in enumerate(winning_order):
        player_elo = players_dict[player]

        # calculate average elo of all players that are still in the game
        if i == 0:  # winner
            better_players_avg_elo = sum(
                [players_dict[p] for p in winning_order[1:]]
            ) / len(winning_order[1:])

            elo_diff = calculate_elo_diff(player_elo, better_players_avg_elo, actual_score=1)
            new_elo[player] += elo_diff

        elif i == len(winning_order) - 1:  # first eliminated player
            worse_players_avg_elo = sum(
                [players_dict[p] for p in winning_order[:-1]]
            ) / len(winning_order[:-1])

            elo_diff = calculate_elo_diff(player_elo, worse_players_avg_elo, actual_score=0)
            new_elo[player] += elo_diff

        else:  # middle players
            better_players = winning_order[:i]  # players that stayed after him
            worse_players = winning_order[i + 1:]  # players that lost before him

            better_players_avg_elo = sum(
                [players_dict[p] for p in better_players]
            ) / len(better_players)
            worse_players_avg_elo = sum(
                [players_dict[p] for p in worse_players]
            ) / len(worse_players)

            worse_elo_k = 32 / num_of_opponents * len(worse_players)
            better_elo_k = 32 / num_of_opponents * len(better_players)

            better_elo_diff = calculate_elo_diff(player_elo, better_players_avg_elo, actual_score=0, k=better_elo_k)
            worse_elo_diff = calculate_elo_diff(player_elo, worse_players_avg_elo, actual_score=1, k=worse_elo_k)
            
            new_elo[player] += better_elo_diff + worse_elo_diff

    return new_elo

def test_elo():
    players_dict = {
        "player1": 1600,
        "player2": 1500,
        "player3": 1500,
        "player4": 1500,
        "player5": 1400,
    }

    winning_order = ["player5", "player4", "player3", "player2", "player1"]
    new_elo = calc_order_elo(players_dict, winning_order)
    print(new_elo)

def small_test_elo():
    players_dict = {
        "player1": 1000,
        "player2": 1200,
    }
    winning_order = ["player2", "player1"]
    new_elo = calc_order_elo(players_dict, winning_order)
    print(new_elo)


if __name__ == "__main__":
    test_elo()
    # small_test_elo()

def test_elo():
    players_dict = {
        "player1": 1600,
        "player2": 1500,
        "player3": 1500,
        "player4": 1500,
        "player5": 1400,
    }

    losing_order = ["player1", "player2", "player3", "player4", "player5"]
    new_elo = calc_order_elo(players_dict, losing_order)
    print(new_elo)

def small_test_elo():
    players_dict = {
        "player1": 1000,
        "player2": 1200,
    }
    losing_order = ["player1", "player2"]
    new_elo = calc_order_elo(players_dict, losing_order)
    print(new_elo)


if __name__ == "__main__":
    test_elo()
    # small_test_elo()
