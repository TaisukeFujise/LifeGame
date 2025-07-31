from typing import List, Tuple, Optional
from . import protocol


class LifeField:
    """Map of a game"""
    def __init__(self, height: int = protocol.HEIGHT, width: int = protocol.WIDTH):
        self.height = height
        self.width = width
        self.cells = []
        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(protocol.DEAD)
            self.cells.append(row)
    
    def place(self, owner: int, pos: Tuple[int, int]) -> bool:
        y, x = pos
        if not self._is_valid_position(y, x):
            return False
        if self.cells[y][x] != protocol.DEAD:
            return False
        self.cells[y][x] = owner
        return True
    
    def _is_valid_position(self, y: int, x: int) -> bool:
        return 0 <= y < self.height and 0 <= x < self.width
    
    def _get_neighbors(self, y: int, x: int) -> List[int]:
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue # 自分自身のセルはスキップ
                ny, nx = y + dy, x + dx
                if self._is_valid_position(ny, nx) and self.cells[ny][nx] > 0:
                    neighbors.append(self.cells[ny][nx])
        return neighbors
    
    def next_generation(self) -> None:
        # 新しい盤面を DEAD で初期化
        new_cells = []
        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                row.append(protocol.DEAD)
            new_cells.append(row)
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self._get_neighbors(y, x)
                alive_count = len(neighbors)
                
                if self.cells[y][x] > 0:  # 生存セル
                    if 2 <= alive_count <= 3:
                        new_cells[y][x] = self.cells[y][x]
                    else:
                        new_cells[y][x] = protocol.DEAD
                else:  # 死亡セル
                    if alive_count == 3:
                        # 多数決で誕生
                        player1_count = neighbors.count(protocol.PLAYER1)
                        player2_count = neighbors.count(protocol.PLAYER2)
                        if player1_count > player2_count:
                            new_cells[y][x] = protocol.PLAYER1
                        elif player1_count < player2_count:
                            new_cells[y][x] = protocol.PLAYER2
                        else:
                            new_cells[y][x] = protocol.DEAD
        
        self.cells = new_cells
    
    def count(self, owner: int) -> int:
        count = 0
        for row in self.cells:
            for cell in row:
                if cell == owner:
                    count += 1
        return count
    
    def get_board_state(self) -> List[List[int]]:
        import copy
        return copy.deepcopy(self.cells)