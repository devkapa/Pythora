import os.path

import PySimpleGUI as sg
import sys
from ctypes import windll

from console.colors import colors, white, lightgreen

windll.shcore.SetProcessDpiAwareness(True)


def icon_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS"):
        path = sys._MEIPASS
    else:
        path = os.path.dirname(os.path.realpath(__file__))

    ico = "Athora.ico"

    return os.path.join(path, ico)


class Console:
    window: sg.Window
    layout = [
        [sg.Multiline(key='ml', disabled=True, background_color='black', text_color='#BBBBBB', font=('Cascadia Mono', 12),
                      expand_x=True, expand_y=True, size=(100, 30), no_scrollbar=True, autoscroll=True,
                      enable_events=True, border_width=0),
         sg.Multiline(key='map', disabled=True, background_color='black', text_color='#BBBBBB',
                      font=('Cascadia Mono', 12), expand_x=True, expand_y=True, size=(30, 30), no_scrollbar=True,
                      enable_events=True, border_width=0, pad=((100, 0), (10, 0))),
         ],
        [sg.Text(key='timer', background_color='black', text_color='white', pad=(0, 0), size=(2, 1),
                 font=('Cascadia Mono', 12), border_width=0, text=">", enable_events=True),
         sg.InputText(key='in', expand_x=True, font=('Cascadia Mono', 12), pad=(0, 0), size=(140, 2),
                      background_color='black', border_width=0, text_color='#00FF00')]
    ]

    def __init__(self, title):
        self.window = sg.Window(title, self.layout, finalize=True, resizable=True, icon=icon_path(),
                                background_color='black')
        self.window['in'].bind("<Return>", "_Enter")
        sys.stdout = self.window['ml']
        self.window['in'].set_focus(force=True)
        self.window['in'].Widget.configure(insertbackground='white')

    def close(self):
        self.window.close()
        sys.exit()

    def set_map_window(self, args):
        self.window['map'].update("")
        self.wrap(args, key='map')

    def timer(self, args, combat):
        if combat:
            self.window['timer'].update(args, text_color='red')
            self.window['timer'].set_size((5, 1))
        else:
            self.window['timer'].update(">", text_color='white')
            self.window['timer'].set_size((2, 1))

    def ginput(self, val=None):
        print(val) if val is not None else None
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                self.close()
                break
            if self.window.find_element_with_focus() is not self.window['in']:
                self.window['in'].set_focus(force=True)
            if event == "in" + "_Enter":
                self.wrap(f"{white}> {lightgreen}{values['in']}" if values['in'] != "" else f"{white}>")
                self.window['in']('')
                return values['in']

    def wrap(self, inp, end=None, key='ml'):
        inp_split = inp.split("||")
        self.next_non_color(inp_split, end, key)

    def next_non_color(self, inp_split, end, key, bg=None):
        inp_split = [item for item in inp_split if item != ""]
        length = len(inp_split)
        i = 0
        while i < length:
            word = inp_split[0]
            if word.startswith("bg."):
                if inp_split[inp_split.index(word) + 1] in colors or word.startswith("#"):
                    self.next_non_color([inp_split[inp_split.index(word) + 1],
                                         inp_split[inp_split.index(word) + 2]], end='', key=key, bg=word.replace("bg.", ""))
                    inp_split.pop(inp_split.index(word) + 1)
                    inp_split.remove(word)
                    i += 3
                else:
                    sg.cprint(inp_split[inp_split.index(word) + 1], window=self.window, key=key,
                              background_color=word.replace("bg.", ""), end='')
                    inp_split.pop(inp_split.index(word) + 1)
                    inp_split.remove(word)
                    i += 2
            elif word in colors or word.startswith("#"):
                if bg is None:
                    sg.cprint(inp_split[inp_split.index(word) + 1], window=self.window,
                              key=key, text_color=word, end='')
                    inp_split.pop(inp_split.index(word) + 1)
                    inp_split.remove(word)
                    i += 2
                else:
                    sg.cprint(inp_split[inp_split.index(word) + 1], window=self.window, key=key,
                              text_color=word, background_color=bg, end='')
                    inp_split.pop(inp_split.index(word) + 1)
                    inp_split.remove(word)
                    i += 2
            else:
                sg.cprint(word, end='', window=self.window, key=key)
                inp_split.remove(word)
                i += 1
        sg.cprint("", window=self.window, key=key, text_color='#BBBBBB') if end is None else None
