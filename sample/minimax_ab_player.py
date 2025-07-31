import copy
import sys 
import os 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lifegame_py import LifePlayer, play_game, protocol, LifeField
import logging

class MinimaxABPlayer(LifePlayer):
    """ 
    ミニマックスプレイヤー（アルファベータ法導入版）
    行動規則：
    ・N世代先読み（アルファベータ法）
    ・「自分のセル数 - 相手のセル数」の差分を最大化
    """
    def __init__(self):
        super().__init__()
    
    def name(self): 
        return 'minimax-lifegame-player-ab'
    
    def initialize(self, field, player_id): 
        super().initialize(field, player_id) 

    def _evaluate_board(self, field: LifeField, player_id: int) -> float:
        """
        現在の盤面を評価する関数。
        「自分のセル数 - 相手のセル数」の差分を返す。
        評価時にはprotocol.SIMULATION_GENERATIONS世代シミュレーションを実行する。
        """
        other_player_id = protocol.PLAYER1 if player_id == protocol.PLAYER2 else protocol.PLAYER2
        
        # SIMULATION_GENERATIONS 世代シミュレーション
        temp_field = LifeField(width=field.width, height=field.height)
        temp_field.cells = copy.deepcopy(field.cells)
        for _ in range(protocol.SIMULATION_GENERATIONS):
            temp_field.next_generation()
        
        my_cells = temp_field.count(player_id)
        opponent_cells = temp_field.count(other_player_id)
        
        return float(my_cells - opponent_cells)

    def _minimax(self, field: LifeField, depth: int, is_maximizing_player: bool, alpha: float, beta: float) -> float:
        """
        ミニマックス探索（アルファベータ法）の再帰関数。
        """
        # ベースケース：探索深さが0になった場合、または盤面が全て埋まった場合
        if depth == 0 or field.count(protocol.DEAD) == 0: 
            return self._evaluate_board(field, self.player_id)

        # 現在の手番のプレイヤーIDを決定
        current_player_id = self.player_id if is_maximizing_player else (protocol.PLAYER1 if self.player_id == protocol.PLAYER2 else protocol.PLAYER2)
        
        # 配置可能な手を生成
        available_moves = []
        for y in range(field.height):
            for x in range(field.width):
                if field.cells[y][x] == protocol.DEAD:
                    available_moves.append((y, x))
        
        # 配置可能な手がない場合（ゲーム終了とみなす）
        if not available_moves:
            return self._evaluate_board(field, self.player_id)

        if is_maximizing_player: # 最大化プレイヤーの番
            max_eval = -float('inf')
            for move_y, move_x in available_moves:
                new_field = LifeField(width=field.width, height=field.height)
                new_field.cells = copy.deepcopy(field.cells)
                new_field.cells[move_y][move_x] = current_player_id
                
                eval = self._minimax(new_field, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: # Beta cutoff
                    break 
            return max_eval
        else: # 最小化プレイヤーの番
            min_eval = float('inf')
            for move_y, move_x in available_moves:
                new_field = LifeField(width=field.width, height=field.height)
                new_field.cells = copy.deepcopy(field.cells)
                new_field.cells[move_y][move_x] = current_player_id
                
                eval = self._minimax(new_field, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: # Alpha cutoff
                    break 
            return min_eval

    def place_cell(self):
        # 探索深さ。この値を変更して読みの深さを調整します。
        # 1は自分の手のみ、2は自分の手+相手の手、3は自分の手+相手の手+自分の手... となる。
        SEARCH_DEPTH = 3

        best_pos = None
        max_score = -float('inf')

        # 全ての空いている位置を試す (自分の手)
        available_moves_for_root = []
        for y in range(self.field.height):
            for x in range(self.field.width):
                if self.field.cells[y][x] == protocol.DEAD:
                    available_moves_for_root.append((y, x))
        
        if not available_moves_for_root:
            raise RuntimeError("No empty positions available")

        for my_y, my_x in available_moves_for_root:
            temp_field = LifeField(width=self.field.width, height=self.field.height)
            temp_field.cells = copy.deepcopy(self.field.cells)
            temp_field.cells[my_y][my_x] = self.player_id

            # ミニマックス探索を呼び出す
            # 自分の手なので、次は相手の番 (is_maximizing_player=False)
            # SEARCH_DEPTH - 1 は、現在の手を除いた残りの探索深さ
            score = self._minimax(temp_field, SEARCH_DEPTH - 1, False, -float('inf'), float('inf'))

            if score > max_score:
                max_score = score
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
    player = MinimaxABPlayer()
    play_game(host, port, player) 

if __name__ == '__main__': 
    import argparse 
    
    parser = argparse.ArgumentParser(
        description="Minimax Player with Alpha-Beta Pruning for Life Game",
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
    
