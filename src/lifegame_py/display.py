from typing import List
from tabulate import tabulate
from . import protocol

# 色の追加
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def make_view(board: List[List[int]], show_grid: bool = True) -> str:
    if show_grid:
        # Create header row with column indices
        headers = [""] + [str(i) for i in range(len(board[0]))]
        
        # Create table data with row indices
        table_data = []
        for y, row in enumerate(board):
            row_data = [str(y)]
            for cell in row:
                if cell == protocol.DEAD:
                    row_data.append(".")
                elif cell == protocol.PLAYER1:
                    row_data.append(f"{RED}1{RESET}")
                elif cell == protocol.PLAYER2:
                    row_data.append(f"{BLUE}2{RESET}")
                else:
                    row_data.append("?")
            table_data.append(row_data)
        
        return tabulate(table_data, headers=headers, tablefmt="grid")
    else:
        # Simple ASCII view without grid
        lines = []
        for row in board:
            line = ""
            for cell in row:
                if cell == protocol.DEAD:
                    line += "."
                elif cell == protocol.PLAYER1:
                    line += f"{RED}1{RESET}"
                elif cell == protocol.PLAYER2:
                    line += f"{BLUE}2{RESET}"
                else:
                    line += "?"
            lines.append(line)
        return "\n".join(lines)


def print_board(board: List[List[int]], title: str = None):
    if title:
        print(f"\n{title}")
    print(make_view(board, show_grid=True))
    
    # Count cells
    count1 = sum(cell == protocol.PLAYER1 for row in board for cell in row)
    count2 = sum(cell == protocol.PLAYER2 for row in board for cell in row)
    print(f"Player 1: {count1} cells, Player 2: {count2} cells")