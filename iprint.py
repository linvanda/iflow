# coding:utf-8
# 彩色打印。仅windows下使用

import ctypes, sys

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

# 颜色定义
FOREGROUND_BLUE = 0x09
FOREGROUND_GREEN = 0x0a
FOREGROUND_RED = 0x0c
FOREGROUND_YELLOW = 0x0e
FOREGROUND_WHITE = 0x0f
FOREGROUND_PINK = 0x0d
FOREGROUND_SKYBLUE = 0x0b

std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)


def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool


# reset to white
def reset_color():
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)


def write(mess, color, new_line = False):
    if new_line:
        mess += "\n"

    set_cmd_text_color(color)
    sys.stdout.write(mess)
    reset_color()


def blue(mess, new_line = False):
    write(mess, FOREGROUND_BLUE, new_line)


def sky_blue(mess, new_line = False):
    write(mess, FOREGROUND_SKYBLUE, new_line)


def green(mess,  new_line = False):
    write(mess, FOREGROUND_GREEN, new_line)


def red(mess, new_line = False):
    write(mess, FOREGROUND_RED, new_line)


def pink(mess, new_line = False):
    write(mess, FOREGROUND_PINK, new_line)


def yellow(mess, new_line = False):
    write(mess, FOREGROUND_YELLOW, new_line)


def white(mess, new_line = False):
    write(mess, FOREGROUND_WHITE, new_line)


def ok(mess):
    green(mess, True)


def warn(mess):
    yellow(mess, True)


def info(mess):
    white(mess, True)


def error(mess):
    red(mess, True)


def say(*words):
    for key, val in words:
        eval(key)(val)

    print
