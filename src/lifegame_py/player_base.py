from typing import Dict, List, Tuple, Any
from .field import LifeField
from . import protocol
import json
import abc
import logging
import socket


class LifePlayer(abc.ABC):
    def __init__(self):
        self.field = None
        self.player_id = None
        self.last_msg = None
        self.placed_cells = 0
    
    def initialize(self, field: LifeField, player_id: int):
        self.field = field
        self.player_id = player_id
        self.placed_cells = 0
        logging.debug(f'Initialized as player {player_id}')
    
    @abc.abstractmethod
    def place_cell(self) -> Tuple[int, int]:
        pass
    
    @abc.abstractmethod
    def name(self) -> str:
        pass
    
    def update(self, json_str: str):
        self.last_msg = json.loads(json_str)
        if "board" in self.last_msg:
            # Update internal field state from server's board
            board = self.last_msg["board"]
            for y in range(len(board)):
                for x in range(len(board[y])):
                    self.field.cells[y][x] = board[y][x]
    
    def get_placement_json(self, position: Tuple[int, int]) -> str:
        return json.dumps({"place": list(position)})


def play_game(host: str, port: int, player: LifePlayer):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        with sock.makefile(mode='rw', buffering=1) as sockfile:
            # Greeting phase
            greeting = sockfile.readline().rstrip()
            logging.debug(f'< {greeting}')
            assert greeting == protocol.greeting
            logging.info(f'connect to server with name {player.name()}')
            sockfile.write(player.name() + '\n')
            
            # Receive field information
            field_info = sockfile.readline()
            field_data = json.loads(field_info)
            field = LifeField(field_data["height"], field_data["width"])
            
            # Determine player ID based on connection order
            player_id = protocol.PLAYER1  # Will be updated by server
            player.initialize(field, player_id)
            
            placement_count = 0
            
            while True:
                # Receive game status
                game_status = sockfile.readline().rstrip()
                
                if game_status == protocol.placement:
                    # Placement phase - player's turn
                    position = player.place_cell()
                    placement_json = player.get_placement_json(position)
                    logging.debug('> ' + placement_json)
                    sockfile.write(placement_json + '\n')
                    placement_count += 1
                elif game_status == protocol.waiting:
                    # Waiting for opponent
                    pass
                elif game_status == protocol.simulation:
                    # Simulation phase started
                    print("Simulation phase started...")
                elif game_status == protocol.you_win:
                    print("You win!")
                    break
                elif game_status == protocol.you_lose:
                    print("You lose!")
                    break
                elif game_status == protocol.draw:
                    print("Draw!")
                    break
                else:
                    raise RuntimeError(f"Unexpected status from server: {game_status}")
                
                # Receive observation/result
                observation = sockfile.readline()
                if not observation:
                    logging.error('Disconnected from server')
                    break
                
                player.update(observation)
                obs_data = json.loads(observation)
                
                # Update player_id if needed
                if "next_player" in obs_data:
                    if placement_count == 0:
                        # First placement determines our player ID
                        player.player_id = obs_data["next_player"]