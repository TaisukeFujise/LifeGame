from .field import LifeField
from . import protocol
import socket
import json
import logging
import sys
import time
from . import display # displayモジュールを追加


class LifeClient:
    def __init__(self, client_id: int, name: str, sockfile):
        self.id = client_id
        self.name = name
        self.placed_count = 0
        self.sockfile = sockfile
    
    def can_place(self) -> bool:
        return self.placed_count < protocol.PLACEMENT_TURNS


class LifeGameControl:
    def __init__(self, field: LifeField):
        self.field = field
        self.clients = []
        self.current_player = 0
    
    def add_client(self, client: LifeClient):
        self.clients.append(client)
    
    def get_player_id(self, client_index: int) -> int:
        return protocol.PLAYER1 if client_index == 0 else protocol.PLAYER2
    
    def place_cell(self, client_index: int, position: tuple):
        client = self.clients[client_index]
        player_id = self.get_player_id(client_index)
        
        if not client.can_place():
            return False
        
        if not self.field.place(player_id, position):
            return False
        
        client.placed_count += 1
        self.current_player = 1 - self.current_player
        
        return {
            "phase": protocol.phase_placement,
            "board": self.field.get_board_state(),
            "next_player": self.get_player_id(self.current_player)
        }
    
    def is_placement_complete(self) -> bool:
        return all(client.placed_count == protocol.PLACEMENT_TURNS for client in self.clients)
    
    def run_simulation(self) -> dict:
        for _ in range(protocol.SIMULATION_GENERATIONS):
            self.field.next_generation()
        
        count1 = self.field.count(protocol.PLAYER1)
        count2 = self.field.count(protocol.PLAYER2)
        
        return {
            "phase": protocol.phase_life_result,
            "board": self.field.get_board_state(),
            "count": {
                "1": count1,
                "2": count2
            }
        }
    
    def get_winner(self) -> int:
        count1 = self.field.count(protocol.PLAYER1)
        count2 = self.field.count(protocol.PLAYER2)

        if count1 > count2:
            return 0  # Player1 (先行) の勝利
        elif count2 > count1:
            return 1  # Player2 (後攻) の勝利
        else:
            # 同数の場合、先行プレイヤー (Player1) の勝利
            return 0


def server_main(host: str, port: int):
    field = LifeField()
    game_control = LifeGameControl(field)
    
    with socket.create_server((host, port), reuse_port=False) as server_sock:
        logging.info(f'Lifegame server listening on {host}:{port}')
        print(f'Lifegame server listening on {host}:{port}')
        sys.stdout.flush()
        
        clients = []
        
        # Accept two clients
        for i in range(2):
            conn, addr = server_sock.accept()
            logging.info(f'Client {i} connected from {addr}')
            print(f'Client {i} connected from {addr}')
            sys.stdout.flush()
            
            sockfile = conn.makefile(mode='rw', buffering=1)
            
            # Send greeting
            sockfile.write(protocol.greeting + '\n')
            sockfile.flush()
            
            # Receive name
            name = sockfile.readline().rstrip()
            logging.info(f'Client {i} name: {name}')
            
            # Create client
            client = LifeClient(i, name, sockfile)
            clients.append(client)
            game_control.add_client(client)
            
            # Send field information
            field_info = json.dumps({
                "height": field.height,
                "width": field.width
            })
            sockfile.write(field_info + '\n')
            sockfile.flush()
        
        # Placement phase
        while not game_control.is_placement_complete():
            current_client = clients[game_control.current_player]
            waiting_client = clients[1 - game_control.current_player]
            
            # Send turn notification
            current_client.sockfile.write(protocol.placement + '\n')
            current_client.sockfile.flush()
            waiting_client.sockfile.write(protocol.waiting + '\n')
            waiting_client.sockfile.flush()
            
            # Receive placement from current player
            placement_json = current_client.sockfile.readline().rstrip()
            if not placement_json:
                logging.error(f'Client {current_client.id} disconnected')
                break
            
            try:
                placement_data = json.loads(placement_json)
                position = tuple(placement_data["place"])
                
                result = game_control.place_cell(current_client.id, position)
                if result is False:
                    # Invalid placement
                    current_client.sockfile.write(protocol.you_lose + '\n')
                    current_client.sockfile.flush()
                    waiting_client.sockfile.write(protocol.you_win + '\n')
                    waiting_client.sockfile.flush()
                    return
                
                # Send result to both clients
                result_json = json.dumps(result) + '\n'
                for client in clients:
                    client.sockfile.write(result_json)
                    client.sockfile.flush()
                
                # --- ここから追加 --- 
                display.print_board(game_control.field.get_board_state(), title="Board after placement")
                # --- ここまで追加 --- 
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logging.error(f'Invalid placement from client {current_client.id}: {e}')
                current_client.sockfile.write(protocol.you_lose + '\n')
                current_client.sockfile.flush()
                waiting_client.sockfile.write(protocol.you_win + '\n')
                waiting_client.sockfile.flush()
                return
        
        # Simulation phase
        for client in clients:
            client.sockfile.write(protocol.simulation + '\n')
            client.sockfile.flush()
        
        # Run simulation step by step
        result = game_control.run_simulation()
        result_json = json.dumps(result) + '\n'
        for client in clients:
            client.sockfile.write(result_json)
            client.sockfile.flush()
        
        display.print_board(game_control.field.get_board_state(), title="Board after simulation")

        # Determine and announce winner
        winner = game_control.get_winner()
        
        if winner == -1:
            for client in clients:
                client.sockfile.write(protocol.draw + '\n')
                client.sockfile.flush()
        else:
            clients[winner].sockfile.write(protocol.you_win + '\n')
            clients[winner].sockfile.flush()
            clients[1 - winner].sockfile.write(protocol.you_lose + '\n')
            clients[1 - winner].sockfile.flush()
        
        # Clean up
        for client in clients:
            client.sockfile.close()
        
        logging.info('Game ended')