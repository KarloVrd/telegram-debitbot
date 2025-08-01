def calculate_elo_diff(player_elo: int, opponent_elo: int, k: int, actual_score: float = 1) -> int:
    '''
    Function calculates elo difference between two players
    k is a constant that determines how much elo will be gained or lost
    '''
    expected_score = 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
    return int(k * (actual_score - expected_score))

def calc_order_elo(players_dict: dict, winning_order: list):
    '''
    Function calculates new elo ratings for every player.
    Each player's k value is provided next to their Elo in players_dict.
    Elo is calculated as if the player won or lost against each player individually.
    Each comparison is made against the original Elo score of the player.
    '''
    original_elo = {player: elo for player, (elo, _) in players_dict.items()}  # Extract original Elo scores
    new_elo = original_elo.copy()

    for i, player in enumerate(winning_order):
        player_elo = original_elo[player]  # Use original Elo for calculations
        player_k = players_dict[player][1]  # Get k value for the player

        for j, opponent in enumerate(winning_order):
            if player == opponent:
                continue

            opponent_elo = original_elo[opponent]  # Use original Elo for opponent
            actual_score = 1 if i < j else 0  # Win if player is ranked higher, else lose
            elo_diff = calculate_elo_diff(player_elo, opponent_elo, actual_score=actual_score, k=player_k)
            new_elo[player] += elo_diff

    return new_elo

def test_elo():
    players_dict = {
        "player1": (1500, 32),
        "player2": (1500, 32),
        "player3": (1500, 32),
        "player4": (1500, 32),
        "player5": (1500, 10)
    }

    winning_order = ["player5", "player4", "player3", "player2", "player1"]
    new_elo = calc_order_elo(players_dict, winning_order)
    print(new_elo)


if __name__ == "__main__":
    test_elo()
    # small_test_elo()


test_elo