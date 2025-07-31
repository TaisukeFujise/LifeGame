import copy
import random
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lifegame_py import LifePlayer, play_game, protocol, LifeField
import logging

# モンテカルロ探索の試行回数
PLAYOUT_COUNT = 100  # この値を大きくするほど精度が上がる

class MonteCarloPlayer(LifePlayer):
    """
    モンテカルロ法プレイヤー
    行動規則：
    ・各合法手について、ランダムにゲームを最後までシミュレーション（プレイアウト）する。
    ・これを指定回数繰り返し、最も勝率の高かった手を選ぶ。
    """
    def __init__(self, seed=0):
        super().__init__()
        self.rng = random.Random(seed or None)

    def name(self):
        return 'montecarlo-lifegame-player'

    def place_cell(self):
        legal_moves = []
        for y in range(self.field.height):
            for x in range(self.field.width):
                if self.field.cells[y][x] == protocol.DEAD:
                    legal_moves.append((y, x))

        if not legal_moves:
            raise RuntimeError("No empty positions available")

        best_move = None
        max_wins = -1

        # 各合法手についてプレイアウトを実行
        for move in legal_moves:
            current_wins = 0
            for _ in range(PLAYOUT_COUNT):
                # 現在の盤面をコピーして、試行用の盤面を作成
                temp_field = LifeField(width=self.field.width, height=self.field.height)
                temp_field.cells = copy.deepcopy(self.field.cells)

                # 最初に試す手を打つ
                temp_field.place(self.player_id, move)
                
                # ゲーム終了までランダムにプレイアウト
                winner = self._playout(temp_field)
                if winner == self.player_id:
                    current_wins += 1
            
            # 最も勝利数の多い手を選ぶ
            if current_wins > max_wins:
                max_wins = current_wins
                best_move = move

        return best_move if best_move is not None else legal_moves[0]

    def _playout(self, field: LifeField) -> int:
        """
        現在の盤面状態から、ゲーム終了までランダムに手を打ち続け、勝者を返す。
        """
        # プレイアウト時のプレイヤーを決定
        turn_player_id = protocol.PLAYER1 if self.player_id == protocol.PLAYER2 else protocol.PLAYER2
        
        # 1. 現在の盤面にあるセル数
        p1_cells = field.count(protocol.PLAYER1)
        p2_cells = field.count(protocol.PLAYER2)
        total_placed_cells = p1_cells + p2_cells

        # 2. 残りの配置ターン数
        remaining_turns = (protocol.PLACEMENT_TURNS * 2) - total_placed_cells

        # 3. 配置可能な空きマスをリストアップ
        empty_cells = []
        for r in range(field.height):
            for c in range(field.width):
                if field.cells[r][c] == protocol.DEAD:
                    empty_cells.append((r, c))
        
        self.rng.shuffle(empty_cells)

        # 4. 残りのターン数だけ、ランダムに配置を行う
        for i in range(remaining_turns):
            if not empty_cells:
                break # 空きマスがなくなったら終了
            
            pos = empty_cells.pop()
            field.place(turn_player_id, pos)
            # プレイヤーを交代
            turn_player_id = protocol.PLAYER1 if turn_player_id == protocol.PLAYER2 else protocol.PLAYER2

        # 5世代シミュレーション
        for _ in range(protocol.SIMULATION_GENERATIONS):
            field.next_generation()

        # 勝敗判定
        p1_count = field.count(protocol.PLAYER1)
        p2_count = field.count(protocol.PLAYER2)

        if p1_count > p2_count:
            return protocol.PLAYER1
        elif p2_count > p1_count:
            return protocol.PLAYER2
        else:
            # 引き分けは先攻(P1)の勝ち
            return protocol.PLAYER1

def main(host, port, seed=0):
    player = MonteCarloPlayer(seed)
    play_game(host, port, player)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Monte Carlo Player for Life Game",
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
