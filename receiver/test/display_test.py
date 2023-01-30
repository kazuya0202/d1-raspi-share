import sys
import tkinter
from PIL import Image, ImageTk
import threading
import time


def show_image():
    # 外から触れるようにグローバル変数で定義
    global item, canvas

    root = tkinter.Tk()
    root.title("test")
    root.geometry("800x600")
    root.attributes("-fullscreen", True)
    img = Image.open("animation_src/1.png")
    img = img.resize((800, 600))
    img = ImageTk.PhotoImage(img)
    canvas = tkinter.Canvas(bg="black", width=800, height=600)
    canvas.place(x=0, y=-60)
    item = canvas.create_image(0, 0, image=img, anchor=tkinter.NW)
    root.mainloop()


# スレッドを立ててtkinterの画像表示を開始する
thread1 = threading.Thread(target=show_image)
thread1.start()

i = 0
while True:

    if i % 2 == 0:
        print("default")
        img = Image.open("animation_src/1.png")
        img = img.resize((800, 600))
        img = ImageTk.PhotoImage(img)
        canvas.itemconfig(item, image=img)
        time.sleep(3)

    if i % 2 == 1:
        print("警告")
        # 切り替えたい画像を定義
        img2 = Image.open("animation_src/1.png")
        img2 = img2.resize((800, 600))
        img2 = ImageTk.PhotoImage(img2)

        # itemを差し替え
        canvas.itemconfig(item, image=img2)
        time.sleep(1)

        # itemをもとに戻す
        img = Image.open("animation_src/2.png")
        img = img.resize((800, 600))
        img = ImageTk.PhotoImage(img)
        canvas.itemconfig(item, image=img)
        time.sleep(1)

        img2 = Image.open("animation_src/3.png")
        img2 = img2.resize((800, 600))
        img2 = ImageTk.PhotoImage(img2)

        # itemを差し替え
        canvas.itemconfig(item, image=img2)
        time.sleep(1)
    i += 1
