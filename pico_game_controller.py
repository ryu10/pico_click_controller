# pico_game_controller. 
# 1. ボタンの状態を読み取り、押し下げ情報を Json メッセージとして USB シリアルへ送信する。
# 2. USB シリアルから Json メッセージを読み取り、LED ストリップを光らせる。

# VSCode MicroPico 環境では、Upload to Pico コマンドを使ってこれらのライブラリファイルを Pico へあらかじめアップロードしておく。

from GameMessages import GameMessages
from LedArray import LedArray
import json

msg_system = GameMessages()
leds = LedArray()

# 初期化
leds.led_array_start()  # LED 実行プロセスをサブコアで起動
leds.led_pattern = 0  # 初期パターンを設定
with leds.lock:
    leds.go = True  # LED ストリップを点灯状態にする

def process_led_message(mesg): # LED メッセージに応じて点滅パターンを切り替え
    # code = json.loads(mesg)
    code = mesg  # 受信したメッセージをそのまま使用
    # print(code)  # デバッグ用に受信したメッセージを表示
    if 'led' in code.keys() and 'pattern' in code['led'].keys(): # 想定するフォーマットかどうか
        val = code['led']['pattern']
        # print(f"Received LED pattern: {val}")
        msg_system.send_message("system", {"mesg": f"Received LED pattern: {val}"})
        if 0 <= val and val <= 3:
            leds.led_pattern = val
            with leds.lock:
                leds.go = False # 現在の点滅パターンルーチンを停止して新しいパターンルーチンを起動
    else:
        print("Unknown message type:", mesg.get("type"))

# メインループ
while True:
    try:
        # ボタンの状態をチェック
        if msg_system.start_button.is_pressed():
            msg_system.send_message("button", {"start_button": True, "pressed": True})
        elif msg_system.main_button.is_pressed():
            msg_system.send_message("button", {"main_button": True, "pressed": True})
        else:
            # USB シリアルからメッセージを受信
            mesg = msg_system.receive_message()
            if mesg is not None:
                # print("Received message:", mesg)
                # 受信したメッセージに基づいて LED ストリップを制御
                process_led_message(mesg)
    except KeyboardInterrupt:
        # print("Stopping LED run thread.")
        msg_system.send_message("system", {"mesg": "KeyboardInterrupt"})
        msg_system.send_message("system", {"mesg": "Stopping LED pattern"})  # LED パターンを停止
        leds.stop()  # LED ストリップを停止
        break
    except Exception as e:
        msg_system.send_message( "error", {"mesg": "An error occurred: {e}"})
        leds.stop()  # エラー時も LED ストリップを停止
        break