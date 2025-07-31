# クライアント側のプログラムについて
## 共通ライブラリ
クライアント側のプログラムは、[document](/doc/document.md)の要件を満たしていればどんな言語で実装されていてもよい。
ソケット通信を行って、適切なJSONを送りさえすればよい。Python の場合は (LifePlayer)[/src/lifegame_py/player_base.py]クラスを継承して使うと便利と思われる。
なお [サーバ側のコード](/src/lifegame_py/server.py)は、プレイヤー側を書く目的では読む必要がない。

### Field
ライフゲームの盤面を保持する．`protocol.py`で定義された`HEIGHT`と`WIDTH`に基づいて初期化される。
[field.py](/src/lifegame_py/field.py)

`display.py` は，ターミナルに `Field` をわかりやすく表示する．
[display.py](/src/lifegame_py/display.py)

### LifePlayer
LifePlayerクラスはAIの雛形となる抽象クラスで、ライフゲームの初期セル配置を決定する`place_cell`メソッドと、プレイヤー名を返す`name`メソッドが抽象メソッドとして定義されている。これらのメソッドは継承したサブクラスで実装されなければならない。
[player_base.py](/src/lifegame_py/player_base.py)

## 単純なAI
上の共通ライブラリの利用例及びソケット通信の例として、単純なAIプログラムを作成し、[random_player.py](/sample/random_player.py) とした。
このプレイヤーは、ライフゲームの盤面にランダムにセルを配置する。

## 操作できるプレイヤー
作成したAIの評価に使う目的で、操作できるプレイヤーとして [manual_player.py](/sample/manual_player.py) を作成した。
これはコマンドライン上でユーザーがセルを配置する場所を指定できる。
