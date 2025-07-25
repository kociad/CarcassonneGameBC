import sys
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from models.gameSession import GameSession
import settings
from utils.loggingConfig import configureLogging
import logging

def configureTestLogging():
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger().handlers.clear()

configureTestLogging()

def run_ai_game(player_names, difficulty):
    ai_names = [f"AI_{difficulty.upper()}_{i+1}" for i in range(len(player_names))]
    session = GameSession(ai_names, lobbyCompleted=True, networkMode='local')
    turn = 0
    while not session.getGameOver():
        current_player = session.getCurrentPlayer()
        if current_player.getIsAI():
            session.playAITurn(current_player)
        else:
            break
        turn += 1
        if turn > 1000:
            print('Infinite loop detected!')
            break
    return [(p.getName(), p.getScore()) for p in session.getPlayers()]

def print_table(results, player_count, file=None):
    header = "\nRESULTS TABLE (scores per player)\n"
    header += "Difficulty | Game | " + " | ".join([f"Player {i+1}" for i in range(player_count)]) + " | Avg Score\n"
    header += "-" * (15 + 12 * (player_count + 1)) + "\n"
    lines = [header]
    for difficulty, games in results.items():
        for game_idx, scores in enumerate(games):
            score_values = [score for _, score in scores]
            avg = sum(score_values) / len(score_values)
            line = f"{difficulty.capitalize():10} | {game_idx+1:4} | " + " | ".join(f"{s:8}" for s in score_values) + f" | {avg:8.2f}\n"
            lines.append(line)
    table = ''.join(lines)
    print(table)
    if file:
        with open(file, 'w') as f:
            f.write(table)

def main():
    player_count = 6
    player_names = [f"Player {i+1}" for i in range(player_count)]
    difficulties = ["easy", "medium", "hard"]
    games_per_difficulty = 5
    results = {d: [] for d in difficulties}
    for difficulty in difficulties:
        print(f"Running {games_per_difficulty} games for difficulty: {difficulty}")
        for game_num in range(games_per_difficulty):
            scores = run_ai_game(player_names, difficulty)
            results[difficulty].append(scores)
            print(f"Finished game {game_num+1} for {difficulty}")
    print_table(results, player_count, file="ai_difficulty_results.txt")

if __name__ == "__main__":
    main() 