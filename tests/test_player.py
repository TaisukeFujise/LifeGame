import pytest
from unittest.mock import MagicMock, patch
from lifegame_py.server import LifeGameControl, LifeClient
from lifegame_py.field import LifeField
from lifegame_py import protocol

# LifeField のモック
@pytest.fixture
def mock_field():
    field = MagicMock(spec=LifeField)
    field.width = protocol.WIDTH
    field.height = protocol.HEIGHT
    field.cells = [[protocol.DEAD for _ in range(protocol.WIDTH)] for _ in range(protocol.HEIGHT)]
    return field

# LifeClient のモック
@pytest.fixture
def mock_client1():
    client = MagicMock(spec=LifeClient)
    client.id = 0
    client.name = "Player1"
    client.placed_count = 0
    client.sockfile = MagicMock()
    client.can_place.return_value = True
    return client

@pytest.fixture
def mock_client2():
    client = MagicMock(spec=LifeClient)
    client.id = 1
    client.name = "Player2"
    client.placed_count = 0
    client.sockfile = MagicMock()
    client.can_place.return_value = True
    return client

@pytest.fixture
def game_control(mock_field):
    return LifeGameControl(mock_field)

def test_add_client(game_control, mock_client1, mock_client2):
    game_control.add_client(mock_client1)
    assert len(game_control.clients) == 1
    assert game_control.clients[0] == mock_client1

    game_control.add_client(mock_client2)
    assert len(game_control.clients) == 2
    assert game_control.clients[1] == mock_client2

    assert game_control.current_player == 0 # 初期プレイヤーは0

def test_get_player_id(game_control):
    assert game_control.get_player_id(0) == protocol.PLAYER1
    assert game_control.get_player_id(1) == protocol.PLAYER2

def test_place_cell_valid(game_control, mock_field, mock_client1, mock_client2):
    game_control.add_client(mock_client1)
    game_control.add_client(mock_client2)

    # place が成功するようモック
    mock_field.place.return_value = True

    position = (5, 5)
    result = game_control.place_cell(mock_client1.id, position)

    mock_field.place.assert_called_once_with(protocol.PLAYER1, position)
    assert mock_client1.placed_count == 1
    assert game_control.current_player == 1 # プレイヤーが切り替わる
    assert result["phase"] == protocol.phase_placement
    assert result["board"] == mock_field.get_board_state.return_value
    assert result["next_player"] == protocol.PLAYER2

def test_place_cell_invalid_position(game_control, mock_field, mock_client1):
    game_control.add_client(mock_client1)

    # place が失敗するようモック
    mock_field.place.return_value = False

    position = (99, 99) # 無効な位置
    result = game_control.place_cell(mock_client1.id, position)

    mock_field.place.assert_called_once_with(protocol.PLAYER1, position)
    assert mock_client1.placed_count == 0 # カウントは増えない
    assert game_control.current_player == 0 # プレイヤーは切り替わらない
    assert result is False

def test_place_cell_placement_limit(game_control, mock_field, mock_client1):
    game_control.add_client(mock_client1)
    mock_client1.placed_count = protocol.PLACEMENT_TURNS # 配置回数上限に達している
    mock_client1.can_place.return_value = False # can_place も False を返すようにモック

    position = (5, 5)
    result = game_control.place_cell(mock_client1.id, position)

    mock_field.place.assert_not_called() # place は呼び出されない
    assert result is False

def test_is_placement_complete(game_control, mock_client1, mock_client2):
    game_control.add_client(mock_client1)
    game_control.add_client(mock_client2)

    assert game_control.is_placement_complete() == False

    mock_client1.placed_count = protocol.PLACEMENT_TURNS
    assert game_control.is_placement_complete() == False # 片方だけでは完了しない

    mock_client2.placed_count = protocol.PLACEMENT_TURNS
    assert game_control.is_placement_complete() == True

def test_run_simulation(game_control, mock_field):
    # count の戻り値を設定
    mock_field.count.side_effect = [10, 5] # Player1: 10, Player2: 5

    result = game_control.run_simulation()

    # next_generation が SIMULATION_GENERATIONS 回呼び出されることを確認
    assert mock_field.next_generation.call_count == protocol.SIMULATION_GENERATIONS
    assert result["phase"] == protocol.phase_life_result
    assert result["board"] == mock_field.get_board_state.return_value
    assert result["count"] == {"1": 10, "2": 5}

def test_get_winner(game_control, mock_field):
    # Player1 が勝つ場合
    mock_field.count.side_effect = [10, 5] # Player1: 10, Player2: 5
    assert game_control.get_winner() == 0

    # Player2 が勝つ場合
    mock_field.count.side_effect = [5, 10] # Player1: 5, Player2: 10
    assert game_control.get_winner() == 1

    # 引き分けの場合
    mock_field.count.side_effect = [7, 7] # Player1: 7, Player2: 7
    assert game_control.get_winner() == -1