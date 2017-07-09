# -*- coding:utf-8 -*-
# @Time     : 2017-06-29 17:46
# @Author   : gck1d6o
# @Site     : 
# @File     : run.py
# @Software : PyCharm


import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = os.path.normcase(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
sys.path.append(BASE_DIR)

# from core import HourseStark
from core import HourseStark


if __name__ == '__main__':
    HourseStark.ArgvHandler(sys.argv)