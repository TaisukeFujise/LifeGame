import pytest
from lifegame_py.field import LifeField
from lifegame_py import protocol

def test_init():
    # デフォルトのサイズで初期化
    field = LifeField()
    assert field.width == protocol.WIDTH
    assert field.height == protocol.HEIGHT
    # 全てのセルがDEADで初期化されていることを確認
    for y in range(field.height):
        for x in range(field.width):
            assert field.cells[y][x] == protocol.DEAD

    # 指定したサイズで初期化
    field = LifeField(width=10, height=15)
    assert field.width == 10
    assert field.height == 15
    for y in range(field.height):
        for x in range(field.width):
            assert field.cells[y][x] == protocol.DEAD

def test_place():
    field = LifeField(width=3, height=3)

    # 有効な位置にセルを配置
    assert field.place(protocol.PLAYER1, (1, 1)) == True
    assert field.cells[1][1] == protocol.PLAYER1

    # 既にセルがある位置には配置できない
    assert field.place(protocol.PLAYER2, (1, 1)) == False
    assert field.cells[1][1] == protocol.PLAYER1 # 変更されていないことを確認

    # 盤面外には配置できない
    assert field.place(protocol.PLAYER1, (-1, 0)) == False
    assert field.place(protocol.PLAYER1, (0, 3)) == False

def test_is_valid_position():
    field = LifeField(width=3, height=3)
    assert field._is_valid_position(0, 0) == True
    assert field._is_valid_position(2, 2) == True
    assert field._is_valid_position(-1, 0) == False
    assert field._is_valid_position(0, 3) == False
    assert field._is_valid_position(3, 0) == False

def test_get_neighbors():
    # Test case 1: Blinker pattern (vertical)
    field = LifeField(width=5, height=5)
    field.place(protocol.PLAYER1, (1, 0))
    field.place(protocol.PLAYER1, (1, 1))
    field.place(protocol.PLAYER1, (1, 2))

    # (1,1) の近傍をテスト
    neighbors = field._get_neighbors(1, 1)
    assert len(neighbors) == 2
    assert neighbors.count(protocol.PLAYER1) == 2

    # (1,0) の近傍をテスト
    neighbors = field._get_neighbors(1, 0)
    assert len(neighbors) == 1
    assert neighbors.count(protocol.PLAYER1) == 1

    # (1,2) の近傍をテスト
    neighbors = field._get_neighbors(1, 2)
    assert len(neighbors) == 1
    assert neighbors.count(protocol.PLAYER1) == 1

    # (0,0) の近傍をテスト
    neighbors = field._get_neighbors(0, 0)
    assert len(neighbors) == 2
    assert neighbors.count(protocol.PLAYER1) == 2

    # Test case 2: Block pattern
    field = LifeField(width=5, height=5)
    field.place(protocol.PLAYER1, (1, 1))
    field.place(protocol.PLAYER1, (1, 2))
    field.place(protocol.PLAYER1, (2, 1))
    field.place(protocol.PLAYER1, (2, 2))

    neighbors = field._get_neighbors(1, 1)
    assert len(neighbors) == 3
    assert neighbors.count(protocol.PLAYER1) == 3

    neighbors = field._get_neighbors(0, 0)
    assert len(neighbors) == 1
    assert neighbors.count(protocol.PLAYER1) == 1

    neighbors = field._get_neighbors(0, 1)
    assert len(neighbors) == 2
    assert neighbors.count(protocol.PLAYER1) == 2

    # Test case 3: 孤立したセル (2,2) の近傍をテスト
    field = LifeField(width=5, height=5)
    neighbors = field._get_neighbors(2, 2)
    assert len(neighbors) == 0

    # Test case 4: 盤面端のセル (0,0) の近傍をテスト
    field = LifeField(width=3, height=3)
    field.place(protocol.PLAYER1, (0, 1))
    field.place(protocol.PLAYER2, (1, 0))
    field.place(protocol.PLAYER1, (1, 1))
    neighbors = field._get_neighbors(0, 0)
    assert len(neighbors) == 3
    assert neighbors.count(protocol.PLAYER1) == 2
    assert neighbors.count(protocol.PLAYER2) == 1

def test_next_generation_blinker():
    field = LifeField(width=5, height=5)
    # 初期状態: 垂直ブリンカー (PLAYER1)
    field.place(protocol.PLAYER1, (1, 0))
    field.place(protocol.PLAYER1, (1, 1))
    field.place(protocol.PLAYER1, (1, 2))

    field.next_generation()
    # 期待される状態: 水平ブリンカー (PLAYER1)
    expected_cells = [[protocol.DEAD for _ in range(5)] for _ in range(5)]
    expected_cells[0][1] = protocol.PLAYER1
    expected_cells[1][1] = protocol.PLAYER1
    expected_cells[2][1] = protocol.PLAYER1

    assert field.get_board_state() == expected_cells

def test_next_generation_block():
    field = LifeField(width=5, height=5)
    # 初期状態: ブロック (安定) (PLAYER1)
    field.place(protocol.PLAYER1, (1, 1))
    field.place(protocol.PLAYER1, (1, 2))
    field.place(protocol.PLAYER1, (2, 1))
    field.place(protocol.PLAYER1, (2, 2))

    field.next_generation()
    # 期待される状態: 変化なし (PLAYER1)
    expected_cells = [[protocol.DEAD for _ in range(5)] for _ in range(5)]
    expected_cells[1][1] = protocol.PLAYER1
    expected_cells[1][2] = protocol.PLAYER1
    expected_cells[2][1] = protocol.PLAYER1
    expected_cells[2][2] = protocol.PLAYER1

    assert field.get_board_state() == expected_cells

def test_next_generation_reproduction_majority_vote():
    field = LifeField(width=3, height=3)
    # 中央のセル (1,1) が DEAD
    # 周囲に PLAYER1 が 2つ、PLAYER2 が 1つ
    field.place(protocol.PLAYER1, (0, 1))
    field.place(protocol.PLAYER1, (1, 0))
    field.place(protocol.PLAYER2, (2, 1))

    field.next_generation()
    # (1,1) は PLAYER1 が多数なので PLAYER1 として誕生するはず
    assert field.cells[1][1] == protocol.PLAYER1

    field = LifeField(width=3, height=3)
    # 中央のセル (1,1) が DEAD
    # 周囲に PLAYER1 が 1つ、PLAYER2 が 2つ
    field.place(protocol.PLAYER1, (0, 1))
    field.place(protocol.PLAYER2, (1, 0))
    field.place(protocol.PLAYER2, (2, 1))

    field.next_generation()
    # (1,1) は PLAYER2 が多数なので PLAYER2 として誕生するはず
    assert field.cells[1][1] == protocol.PLAYER2

def test_count():
    field = LifeField(width=3, height=3)
    field.place(protocol.PLAYER1, (0, 0))
    field.place(protocol.PLAYER1, (1, 1))
    field.place(protocol.PLAYER2, (2, 2))

    assert field.count(protocol.PLAYER1) == 2
    assert field.count(protocol.PLAYER2) == 1
    assert field.count(protocol.DEAD) == 6 # 9 - 2 - 1

def test_get_board_state():
    field = LifeField(width=2, height=2)
    field.place(protocol.PLAYER1, (0, 0))
    expected_state = [
        [protocol.PLAYER1, protocol.DEAD],
        [protocol.DEAD, protocol.DEAD]
    ]
    assert field.get_board_state() == expected_state

    # 状態がコピーであることを確認 (元のオブジェクトへの参照ではない)
    retrieved_state = field.get_board_state()
    retrieved_state[0][0] = protocol.PLAYER2
    assert field.cells[0][0] == protocol.PLAYER1 # 元のフィールドは変更されていない