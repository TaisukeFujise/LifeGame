import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lifegame_py import LifePlayer, play_game, protocol
import random
import logging


class RandomPlayer(LifePlayer):
    def __init__(self, seed=0):
        super().__init__()
        self.rng = random.Random(seed or None)
        self.available_positions = []
    
    def name(self):
        return 'random-lifegame-player'
    
    def initialize(self, field, player_id):
        super().initialize(field, player_id)
        # Create list of all available positions
        self.available_positions = [
            (y, x) 
            for y in range(field.height) 
            for x in range(field.width)
        ]
        self.rng.shuffle(self.available_positions)
    
    def place_cell(self):
        # Find an empty position randomly
        while self.available_positions:
            pos = self.available_positions.pop()
            if self.field.cells[pos[0]][pos[1]] == protocol.DEAD:
                return pos
        
        # Fallback - shouldn't happen in normal gameplay
        for y in range(self.field.height):
            for x in range(self.field.width):
                if self.field.cells[y][x] == protocol.DEAD:
                    return (y, x)
        
        raise RuntimeError("No empty positions available")


def main(host, port, seed=0):
    player = RandomPlayer(seed)
    play_game(host, port, player)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Random Player for Life Game",
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
        "--seed", type=int, default=0,
        help="Random seed of the player (0 for urandom)",
    )
    parser.add_argument(
        "--verbose", action='store_true',
        help="verbose output",
    )
    args = parser.parse_args()
    
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format=FORMAT, level=level, force=True)
    
    main(args.host, args.port, seed=args.seed)