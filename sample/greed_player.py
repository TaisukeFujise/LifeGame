import copy
import sys 
import os 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lifegame_py import LifePlayer, play_game, protocol, LifeField
import logging

class GreedPlayer(LifePlayer):
    """ 
    貪欲プレイヤー（Greedy Player）
    行動規則：
    ・3世代先読み
    ・「自分のセル数 - 相手のセル数」の差分を最大化
    ・次の相手の手を考慮しない。
    """
    def __init__(self):
        super().__init__()
    
    def name(self): 
        return 'greed-lifegame-player'
    
    def initialize(self, field, player_id): 
        super().initialize(field, player_id) 

    def place_cell(self):
        best_pos = None
        max_score = -float('inf') # スコアを負の無限大で初期化

        # 相手プレイヤーのIDを決定
        other_player_id = protocol.PLAYER1 if self.player_id == protocol.PLAYER2 else protocol.PLAYER2

        # 全ての空いている位置を試す
        for y in range(self.field.height):
            for x in range(self.field.width):
                if self.field.cells[y][x] == protocol.DEAD:
                    # 試行用のフィールドを作成し、現在の状態をコピー
                    temp_field = LifeField(width=self.field.width, height=self.field.height)
                    temp_field.cells = copy.deepcopy(self.field.cells)
                    # 仮にセルを配置
                    temp_field.cells[y][x] = self.player_id

                    # SIMULATION_GENERATIONS 世代シミュレーション
                    for _ in range(protocol.SIMULATION_GENERATIONS):
                        temp_field.next_generation()
                    
                    current_my_cells = temp_field.count(self.player_id)
                    current_opponent_cells = temp_field.count(other_player_id)

                    # 最も良い配置を更新 (自分のセル数 - 相手のセル数 の差分を最大化)
                    current_score = current_my_cells - current_opponent_cells
                    if current_score > max_score:
                        max_score = current_score
                        best_pos = (y, x)
        
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
    player = GreedPlayer()
    play_game(host, port, player) 

if __name__ == '__main__': 
    import argparse 
    
    parser = argparse.ArgumentParser(
        description="Greed Player for Life Game",
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
    
