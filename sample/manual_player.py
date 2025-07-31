import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lifegame_py import LifePlayer, play_game, protocol, print_board
import logging
import time

def clear_screen():
    """Clear the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def input_position():
    """Get position input from user"""
    print("Please input cell position (row, col) in [0, 5]")
    while True:
        try:
            y = int(input("row = "))
            x = int(input("col = "))
            if 0 <= y < protocol.HEIGHT and 0 <= x < protocol.WIDTH:
                return (y, x)
            else:
                print(f"Position must be in range [0, {protocol.HEIGHT-1}] x [0, {protocol.WIDTH-1}]")
        except ValueError:
            print("Please enter valid integers")


class ManualPlayer(LifePlayer):
    def __init__(self):
        super().__init__()
    
    def name(self):
        return 'manual-lifegame-player'
    
    def place_cell(self):
        clear_screen()
        # Show current board state
        if self.last_msg and "board" in self.last_msg:
            print(f"--- Game Phase: Placement ---")
            print_board(self.last_msg["board"], f"Current board (You are Player {self.player_id})")
            print(f"Current turn: You (Player {self.player_id})")
        else:
            print(f"You are Player {self.player_id})")
            print(f"Current turn: You (Player {self.player_id})")
        
        # Get position from user
        while True:
            pos = input_position()
            # Check if position is empty
            if self.field.cells[pos[0]][pos[1]] == protocol.DEAD:
                return pos
            else:
                print("That position is already occupied. Please choose an empty cell.")
    
    def update(self, json_str):
        super().update(json_str)
        
        # Show game progress
        if self.last_msg:
            if self.last_msg.get("phase") == protocol.phase_placement:
                clear_screen()
                # During placement phase
                print("\n" + "="*50)
                print(f"--- Game Phase: Placement ---")
                print_board(self.last_msg["board"], "Board after placement")
                if self.last_msg.get("next_player") == self.player_id:
                    print(f"Current turn: You (Player {self.player_id})")
                else:
                    print(f"Current turn: Opponent")
                # time.sleep(2)
            
            elif self.last_msg.get("phase") == protocol.phase_life_result:
                time.sleep(3)
                clear_screen()
                # After simulation
                print("\n" + "="*50)
                print(f"--- Game Phase: Simulation Result ---")
                print("SIMULATION COMPLETE!")
                print_board(self.last_msg["board"], "Final board state")
                count = self.last_msg.get("count", {})
                print(f"Final scores:")
                print(f"Player 1: {count.get('1', 0)} cells")
                print(f"Player 2: {count.get('2', 0)} cells")


def main(host, port):
    player = ManualPlayer()
    play_game(host, port, player)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manual Player for Life Game",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "host",
        help="Hostname of the server, e.g., localhost",
    )
    parser.add_argument(
        "port",
        type=int,
        help="Port of the server, e.g., 2000",
    )
    parser.add_argument(
        "--verbose", action='store_true',
        help="verbose output",
    )
    args = parser.parse_args()
    
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format=FORMAT, level=level, force=True)
    
    main(args.host, args.port)