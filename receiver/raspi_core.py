# -*- coding: utf-8 -*-

"""
raspihat_TXsample001.py : im_wireless.pyを使用し、受信データを出力かつテキスト保存
                          子機へACKを返す
                          Crlt+Cでプログラムを終了する
(C)2019 interplan Corp.

Ver. 0.010    2019/07/08   test version

本ソフトウェアは無保証です。
本ソフトウェアの不具合により損害が発生した場合でも補償は致しません。
改変・流用はご自由にどうぞ。
"""
import threading
import time
import tkinter
from datetime import datetime
from pathlib import Path

import RPi.GPIO as GPIO
from configs import Config
from flags import DisplayFlags
from func import parse_data
from im920hat_module import im_wireless as imw
from PIL import Image, ImageTk


def build_gui():
    global item, canvas

    root = tkinter.Tk()
    root.title("GUI")
    root.geometry("{0}x{1}".format(Config.DISPLAY_WIDTH, Config.DISPLAY_HEIHGT))
    root.attributes("-fullscreen", True)
    # img = load_image(
    #     illust_src_root / "animation_src/sleep.png", size=Config.DISPLAY_SIZE
    # )
    img = Image.open(illust_src_root / "animation_src/sleep.png")
    img = ImageTk.PhotoImage(img)
    canvas = tkinter.Canvas(
        bg="black", width=Config.DISPLAY_WIDTH, height=Config.DISPLAY_HEIHGT
    )
    canvas.place(x=0, y=0)
    item = canvas.create_image(0, 0, image=img, anchor=tkinter.NW)
    root.mainloop()


def display_animation(level: int):
    global item, canvas, animation_loop

    # ライト、電圧スピーカーON
    p_sound.start(50)
    p_sound.ChangeFrequency(261)
    GPIO.output(led_pin, GPIO.HIGH)

    # イラストアニメーション
    images = []
    for i in [1, 2, 3]:
        # img = load_image(
        #     illust_src_root / f"animation_src/level{level}/{i}.png",
        #     size=Config.DISPLAY_SIZE,
        # )
        img = Image.open(illust_src_root / f"animation_src/level{level}/{i}.png")
        img_disp = ImageTk.PhotoImage(img)
        images.append(img_disp)

    while animation_loop:
        # for img_disp in [img1_disp, img2_disp, img3_disp]:
        for img_disp in images:
            canvas.itemconfig(item, image=img_disp)
            time.sleep(1)

    # ライト、電圧スピーカーOFF
    GPIO.output(led_pin, GPIO.LOW)
    p_sound.stop()


def display_sleep():
    global item, canvas, animation_loop

    # img = load_image(
    #     illust_src_root / "animation_src/sleep.png", size=Config.DISPLAY_SIZE
    # )
    img = Image.open(illust_src_root / "animation_src/sleep.png")
    img_disp = ImageTk.PhotoImage(img)
    while animation_loop:
        canvas.itemconfig(item, image=img_disp)
        time.sleep(1)


def main():
    global item, canvas, animation_loop

    iwc = imw.IMWireClass(SLAVE_ADR)  # classの初期化

    # アニメーションを繰り返し続けるためにスレッド化
    anim_thread = threading.Thread(target=display_sleep)
    anim_thread.start()

    # logの内容を実行時間で区切ってわかりやすく
    with open(FILE_NAME, "a") as f:
        runtime = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
        f.write(f"\n{runtime}\n")

    try:
        while True:
            rx_data = iwc.Read_920()  # 受信処理
            if isinstance(rx_data, int):
                print("rx_data is integer")
                continue
            if len(rx_data) <= 0:  # 受信してない時は''が返り値 (長さ0)
                continue

            print(rx_data, end="")  # 受信データを画面表示
            with open(FILE_NAME, "a") as f:  # ファイルを開く
                f.write(rx_data)  # 1dataをファイル末尾に書き込み

            if len(rx_data) < 11:  # 11に満たないならcontinue
                continue

            # 長さが11以上あるならデータを受信したと判断できる
            # - 11は受信データのノード番号+RSSI等の長さ
            if rx_data[2] == "," and rx_data[7] == "," and rx_data[10] == ":":
                data = parse_data(rx_data)
                print(f"received: {data}")
                data_upper = data.upper()

                # 空で送られてきた時は無視する
                if data_upper == "00":
                    continue

                animation_loop = False  # アニメーションを止める
                if anim_thread:
                    anim_thread.join()  # スレッドが止まるまで待つ

                # 次に再生するアニメーションのスレッドを立てて再度アニメーションを開始させる
                animation_loop = True
                if data_upper == DisplayFlags.DISP_LEVEL3:
                    anim_thread = threading.Thread(target=display_animation, args=(3,))

                elif data_upper == DisplayFlags.DISP_LEVEL4:
                    anim_thread = threading.Thread(target=display_animation, args=(4,))

                elif data_upper == DisplayFlags.DISP_LEVEL5:
                    anim_thread = threading.Thread(target=display_animation, args=(5,))

                elif data_upper == DisplayFlags.DISP_SLEEP:
                    anim_thread = threading.Thread(target=display_sleep)

                else:
                    # アニメーションの変更なし
                    anim_thread = None

                if anim_thread:
                    anim_thread.start()

                # * 2022/12/20 現状送り返す必要がないためコメントアウト
                # rxid = rx_data[3:7]  # 子機(送信機)のIDを抽出
                # txbuf = "TXDA" + rxid  # コマンドにCR+LFはいらない
                # print(">", txbuf)
                # iwc.Write_920(txbuf)  # コマンドを送信
    except KeyboardInterrupt:  # Ctrl + C End
        iwc.gpio_clean()
        print("END")


if __name__ == "__main__":
    # データログ
    FILE_NAME = "./log.txt"

    # i2c
    # * 2022/11/29 `i2cdetect -y 1` で確認して30が使われていたから多分OK
    SLAVE_ADR = 0x30  # hatのI2Cアドレスは0x30 ~ 0x33

    # ライト、電圧スピーカーのセットアップ
    pin = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    led_pin = 15
    GPIO.setup(led_pin, GPIO.OUT, initial=GPIO.LOW)
    p_sound = GPIO.PWM(pin, 1)

    animation_loop = True

    # スレッドを立ててtkinterの画像表示を開始する
    gui_thread = threading.Thread(target=build_gui)
    gui_thread.start()

    illust_src_root = Path(__file__).parent
    main()
