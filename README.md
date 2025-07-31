# life_game
二人対戦型ライフゲーム（Conway's Game of Life のバリエーション）。
クライアントプログラム作成用の詳しい仕様は[こちら](/doc/lifegame_doc.md)

## ルール
1. 6×6のマス目を使用。各マスは死亡(0)、プレイヤー1所有(1)、プレイヤー2所有(2)のいずれかの状態を持つ。
2. 配置フェーズ：プレイヤー1から交互に6回ずつ、計12回セルを配置する。
3. シミュレーションフェーズ：Conway's Game of Lifeのルールを3世代分実行する。
   * 生存セルは隣接生存セル数が2または3の場合のみ生存継続
   * 死亡セルは隣接生存セル数が3の場合に誕生（多数派のプレイヤーが所有）
4. 最終的に所有セル数が多いプレイヤーが勝利。同数の場合は引き分け。

## ディレクトリ構成
- [/doc/lifegame_doc.md](/doc/lifegame_doc.md) 詳細仕様書
- [/src/lifegame_py](/src/lifegame_py) ライフゲームライブラリ
- [/sample_life](/sample_life) サーバーとプレイヤーのサンプル

## 実行
ライフゲームサーバを起動する。
```
$ python3 sample_life/server.py localhost 2001
```
クライアントを2つ接続する。
```
$ python3 sample_life/random_player.py localhost 2001
$ python3 sample_life/manual_player.py localhost 2001
```

人間プレイ用の[manual_player.py](/sample_life/manual_player.py)では、盤面が表示され配置位置を入力できる。
```
Current board (You are Player 1)
+---+---+---+---+---+---+---+
|   | 0 | 1 | 2 | 3 | 4 | 5 |
+---+---+---+---+---+---+---+
| 0 | . | . | . | . | . | . |
+---+---+---+---+---+---+---+
| 1 | . | 1 | . | . | 2 | . |
+---+---+---+---+---+---+---+
| 2 | . | . | . | . | . | . |
+---+---+---+---+---+---+---+
| 3 | . | . | . | . | . | . |
+---+---+---+---+---+---+---+
| 4 | . | . | . | . | . | . |
+---+---+---+---+---+---+---+
| 5 | . | . | . | . | . | . |
+---+---+---+---+---+---+---+
Player 1: 1 cells, Player 2: 1 cells
Please input cell position (row, col) in [0, 5]
row = 2
col = 3
```
