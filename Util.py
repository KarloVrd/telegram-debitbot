
def calculate_elo_diff(player_elo: int, opponent_elo: int, actual_score: float = 1, k: int = 32) -> int:
    '''
    Function calculates elo difference between two players
    k is a constant that determines how much elo will be gained or lost
    '''
    expected_score = 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
    return int(k * (actual_score - expected_score))

def calc_order_elo(players_dict: dict, losing_order: list):
    '''
    Function calculates new elo ratings for every player
    due to nature of the game, players are losing the game until there is last player standing
    For each player we calculate:
    - average elo of all players that were eliminated before him
    - average elo of all players that were in the game after him
    
    Only the first and last player have different calculations, 
    they only take into account one of the averages

    '''
    new_elo = players_dict.copy()
    num_of_opponents = len(losing_order) - 1

    for i, player in enumerate(losing_order):
        player_elo = players_dict[player]

        # calculate average elo of all players that are still in the game
        if i == 0: # first eliminated player
            lost_avg_elo = sum(
                [players_dict[p] for p in losing_order[1:]]
            ) / len(losing_order[1:])

            elo_diff = calculate_elo_diff(player_elo, lost_avg_elo, actual_score=0)
            new_elo[player] += elo_diff

        elif i == len(losing_order) - 1: # winner
            won_avg_elo = sum(
                [players_dict[p] for p in losing_order[:i]]
            ) / len(losing_order[:i])

            elo_diff = calculate_elo_diff(player_elo, won_avg_elo, actual_score=1)
            new_elo[player] += elo_diff

        else: # middle players
            won_players = losing_order[:i] # players that were eliminated before him
            lost_players = losing_order[i + 1:] # players that were eliminated after him

            won_avg_elo = sum(
                [players_dict[p] for p in won_players]
            ) / len(won_players)
            lost_avg_elo = sum(
                [players_dict[p] for p in lost_players]
            ) / len(lost_players)

            lost_elo_k = 32 / num_of_opponents * len(lost_players)
            won_elo_k = 32 / num_of_opponents * len(won_players)

            lost_elo_diff = calculate_elo_diff(player_elo, won_avg_elo, actual_score=1, k=won_elo_k)
            won_elo_diff = calculate_elo_diff(player_elo, lost_avg_elo, actual_score=0, k=lost_elo_k)
            
            new_elo[player] += lost_elo_diff + won_elo_diff

    return new_elo

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
