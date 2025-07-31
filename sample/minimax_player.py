import copy
import sys 
import os 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lifegame_py import LifePlayer, play_game, protocol, LifeField
import logging

class MinimaxPlayer(LifePlayer):
    """ 
    ミニマックスプレイヤー
    行動規則：
    ・3世代先読み
    ・「自分のセル数 - 相手のセル数」の差分を最大化
    ・相手の次の手を考慮する。
        ・自分のセルを仮に配置した後、相手が「自分のセル数 - 相手のセル数」を最小化するような最適な手をシミュレートする。
        ・相手の最適な手までシミュレートした後、さらにSIMULATION_GENERATIONS（プロトコルで定義された世代数）分、ライフゲームのシミュレーションを進める。
        ・最終的な盤面で「自分のセル数 - 相手のセル数」を計算する。
    """
    def __init__(self):
        super().__init__()
    
    def name(self): 
        return 'minimax-lifegame-player'
    
    def initialize(self, field, player_id): 
        super().initialize(field, player_id) 

    def place_cell():
        best_pos = None
        max_score = -float('inf') # スコアを負の無限大で初期化
    
    def name(self): 
        return 'minimax-lifegame-player'
    
    def initialize(self, field, player_id): 
        super().initialize(field, player_id) 

    def place_cell(self):
        best_pos = None
        max_score = -float('inf') # スコアを負の無限大で初期化

        other_player_id = protocol.PLAYER1 if self.player_id == protocol.PLAYER2 else protocol.PLAYER2

        # 全ての空いている位置を試す (自分の手)
        for my_y in range(self.field.height):
            for my_x in range(self.field.width):
                if self.field.cells[my_y][my_x] == protocol.DEAD:
                    # --- 1. 自分のセルを仮に配置した後のボードを作成 ---
                    temp_field_after_my_move = LifeField(width=self.field.width, height=self.field.height)
                    temp_field_after_my_move.cells = copy.deepcopy(self.field.cells)
                    temp_field_after_my_move.cells[my_y][my_x] = self.player_id

                    # --- 2. 相手の最適な応答をシミュレート ---
                    # 相手も自分のスコア（相手のセル数 - 自分のセル数）を最大化しようとすると仮定する。
                    # これは、私のスコア（自分のセル数 - 相手のセル数）を最小化する手となる。
                    
                    best_opponent_response_field = None
                    min_my_score_after_opponent_move = float('inf') # 相手が選ぶ手によって、私のスコアが最小になる値

                    opponent_possible_moves_found = False
                    for opp_y in range(temp_field_after_my_move.height):
                        for opp_x in range(temp_field_after_my_move.width):
                            if temp_field_after_my_move.cells[opp_y][opp_x] == protocol.DEAD:
                                opponent_possible_moves_found = True
                                
                                temp_field_after_opponent_move = LifeField(width=self.field.width, height=self.field.height)
                                temp_field_after_opponent_move.cells = copy.deepcopy(temp_field_after_my_move.cells)
                                temp_field_after_opponent_move.cells[opp_y][opp_x] = other_player_id

                                # SIMULATION_GENERATIONS 世代シミュレーション 
                                for _ in range(protocol.SIMULATION_GENERATIONS):
                                    temp_field_after_opponent_move.next_generation()
                                
                                # 相手の視点でのスコアを評価 (相手のセル数 - 自分のセル数)
                                current_my_cells_after_sim = temp_field_after_opponent_move.count(self.player_id)
                                current_opponent_cells_after_sim = temp_field_after_opponent_move.count(other_player_id)
                                
                                # 相手は自分のスコアを最大化する
                                my_score_if_opponent_chooses_this = current_my_cells_after_sim - current_opponent_cells_after_sim

                                if my_score_if_opponent_chooses_this < min_my_score_after_opponent_move:
                                    min_my_score_after_opponent_move = my_score_if_opponent_chooses_this
                                    best_opponent_response_field = temp_field_after_opponent_move # 相手が選んだ後のボード

                    # --- 3. 相手が最適な応答をした後のボードで最終評価 --- 
                    # 相手がセルを配置する場所が見つからなかった場合（ボードが満杯など）の考慮
                    if not opponent_possible_moves_found:
                        # 相手が配置できない場合、自分の配置後のボードで評価
                        final_field_for_evaluation = temp_field_after_my_move
                        # ただし、この場合も SIMULATION_GENERATIONS を実行する必要がある
                        for _ in range(protocol.SIMULATION_GENERATIONS):
                            final_field_for_evaluation.next_generation()
                    else:
                        final_field_for_evaluation = best_opponent_response_field

                    current_my_cells = final_field_for_evaluation.count(self.player_id)
                    current_opponent_cells = final_field_for_evaluation.count(other_player_id)

                    current_score = current_my_cells - current_opponent_cells
                    if current_score > max_score:
                        max_score = current_score
                        best_pos = (my_y, my_x)
        
        # 最適な位置が見つからなかった場合（全てのセルが埋まっているなど）のフォールバック
        if best_pos is None:
            # 念のため、空いている最初のセルを返す
            for y in range(self.field.height):
                for x in range(self.field.width):
                    if self.field.cells[y][x] == protocol.DEAD:
                        return (y, x)
            raise RuntimeError("No empty positions available")

        return best_pos

def main(host, port , seed=0): 
    player = MinimaxPlayer()
    play_game(host, port, player) 

if __name__ == '__main__': 
    import argparse 
    
    parser = argparse.ArgumentParser(
        description="Minimax Player for Life Game",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "host",
        help="Hostname of the server, e.g., localhost"
    )
    parser.add_argument(
        "port",
        type=int,
        help="Port of the server, e.g., 2000"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="verbose output"
    )
    args = parser.parse_args()

    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format=FORMAT, level=level, force=True)

    main(args.host, args.port, args.seed)
    
