import pytest
from unittest.mock import MagicMock, patch, mock_open
from lifegame_py.player_base import LifePlayer, play_game
from lifegame_py.field import LifeField
from lifegame_py import protocol
import json

# Mock LifePlayer の実装
class MockLifePlayer(LifePlayer):
    def __init__(self, actions=None):
        super().__init__()
        self._actions = actions if actions is not None else []
        self._action_index = 0

    def place_cell(self):
        if self._action_index < len(self._actions):
            action = self._actions[self._action_index]
            self._action_index += 1
            return action
        return (0, 0) # デフォルト

    def name(self):
        return "MockPlayer"

@pytest.fixture
def mock_socket_and_sockfile():
    with patch('socket.socket') as mock_sock_class:
        mock_sock = mock_sock_class.return_value
        mock_sockfile = MagicMock()
        mock_sock.makefile.return_value = mock_sockfile
        # コンテキストマネージャーとしても動作するように設定
        mock_sock.__enter__ = MagicMock(return_value=mock_sock)
        mock_sock.__exit__ = MagicMock(return_value=None)
        mock_sockfile.__enter__ = MagicMock(return_value=mock_sockfile)
        mock_sockfile.__exit__ = MagicMock(return_value=None)
        yield mock_sock, mock_sockfile

@pytest.fixture
def player_instance():
    return MockLifePlayer()

def test_player_initialize(player_instance):
    field = LifeField(width=10, height=10)
    player_instance.initialize(field, protocol.PLAYER1)
    assert player_instance.field == field
    assert player_instance.player_id == protocol.PLAYER1
    assert player_instance.placed_cells == 0

def test_player_update(player_instance):
    field = LifeField(width=2, height=2)
    player_instance.initialize(field, protocol.PLAYER1)

    # ボード更新メッセージをシミュレート
    board_state = [
        [protocol.PLAYER1, protocol.DEAD],
        [protocol.DEAD, protocol.PLAYER2]
    ]
    update_msg = json.dumps({"board": board_state})
    player_instance.update(update_msg)

    assert player_instance.last_msg == {"board": board_state}
    assert player_instance.field.cells == board_state

def test_player_get_placement_json(player_instance):
    pos = (5, 7)
    expected_json = json.dumps({"place": [5, 7]})
    assert player_instance.get_placement_json(pos) == expected_json

def test_play_game_greeting_and_name_exchange(mock_socket_and_sockfile):
    mock_sock, mock_sockfile = mock_socket_and_sockfile
    player = MockLifePlayer()

    # サーバーからの応答をモック
    # readline()の戻り値に対してrstrip()が呼び出されるので、
    # 改行文字を含む文字列を返す
    mock_sockfile.readline.side_effect = [
        protocol.greeting + '\n', # 挨拶
        json.dumps({"height": 20, "width": 20}) + '\n', # フィールド情報
        protocol.placement + '\n', # 配置フェーズ
        json.dumps({"board": [[0]]}) + '\n', # ボード更新
        protocol.you_win + '\n', # ゲーム終了
    ]

    # play_game を実行
    play_game("localhost", 12345, player)

    # 接続とファイル作成の確認
    mock_sock.connect.assert_called_once_with(("localhost", 12345))
    mock_sock.makefile.assert_called_once_with(mode='rw', buffering=1)

    # プレイヤー名の送信確認
    mock_sockfile.write.assert_any_call(player.name() + '\n')

def test_play_game_placement_phase(mock_socket_and_sockfile):
    mock_sock, mock_sockfile = mock_socket_and_sockfile
    # place_cell が (1,1) を返すように設定
    player = MockLifePlayer(actions=[(1, 1)])

    mock_sockfile.readline.side_effect = [
        protocol.greeting + '\n',
        json.dumps({"height": 20, "width": 20}) + '\n',
        protocol.placement + '\n', # 配置フェーズ
        json.dumps({"board": [[0]]}) + '\n', # ボード更新
        protocol.you_win + '\n', # ゲーム終了
    ]

    play_game("localhost", 12345, player)

    # place_cell が呼び出され、その結果が送信されたことを確認
    expected_placement_json = player.get_placement_json((1, 1))
    mock_sockfile.write.assert_any_call(expected_placement_json + '\n')

def test_play_game_simulation_phase(mock_socket_and_sockfile):
    mock_sock, mock_sockfile = mock_socket_and_sockfile
    player = MockLifePlayer()

    mock_sockfile.readline.side_effect = [
        protocol.greeting + '\n',
        json.dumps({"height": 20, "width": 20}) + '\n',
        protocol.simulation + '\n', # シミュレーションフェーズ
        json.dumps({"board": [[0]]}) + '\n', # ボード更新
        protocol.you_win + '\n', # ゲーム終了
    ]

    play_game("localhost", 12345, player)

    # シミュレーションフェーズでは place_cell が呼び出されないことを確認
    assert player._action_index == 0

def test_play_game_game_end_conditions(mock_socket_and_sockfile):
    mock_sock, mock_sockfile = mock_socket_and_sockfile
    player = MockLifePlayer()

    # you_win のテスト
    mock_sockfile.readline.side_effect = [
        protocol.greeting + '\n',
        json.dumps({"height": 20, "width": 20}) + '\n',
        protocol.you_win + '\n',
    ]
    with patch('builtins.print') as mock_print:
        play_game("localhost", 12345, player)
        mock_print.assert_any_call("You win!")

    # you_lose のテスト
    mock_sockfile.readline.side_effect = [
        protocol.greeting + '\n',
        json.dumps({"height": 20, "width": 20}) + '\n',
        protocol.you_lose + '\n',
    ]
    with patch('builtins.print') as mock_print:
        play_game("localhost", 12345, player)
        mock_print.assert_any_call("You lose!")

    # draw のテスト
    mock_sockfile.readline.side_effect = [
        protocol.greeting + '\n',
        json.dumps({"height": 20, "width": 20}) + '\n',
        protocol.draw + '\n',
    ]
    with patch('builtins.print') as mock_print:
        play_game("localhost", 12345, player)
        mock_print.assert_any_call("Draw!")

def test_play_game_player_id_update(mock_socket_and_sockfile):
    mock_sock, mock_sockfile = mock_socket_and_sockfile
    player = MockLifePlayer(actions=[(0,0)]) # 最初の配置でIDが決定される

    mock_sockfile.readline.side_effect = [
        protocol.greeting + '\n',
        json.dumps({"height": 20, "width": 20}) + '\n',
        protocol.placement + '\n', # 配置フェーズ
        json.dumps({"board": [[0]], "next_player": protocol.PLAYER2}) + '\n', # ボード更新とID通知
        protocol.you_win + '\n', # ゲーム終了
    ]

    play_game("localhost", 12345, player)
    # placement_count == 1 の後でプレイヤーIDが更新されることを確認
    assert player.player_id == protocol.PLAYER2