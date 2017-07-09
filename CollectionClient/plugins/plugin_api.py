# -*- coding:utf-8 -*-
# @Time     : 2017-06-30 11:21
# @Author   : gck1d6o
# @Site     : 
# @File     : plugin_api.py
# @Software : PyCharm


def linux_sys_info():
    """
    获取linux系统信息
    :return:
    """
    from plugins.linux.sysinfo import LinuxInfo
    info = LinuxInfo()
    return info.collect


def windows_sys_info():
    """
    获取windows系统信息
    :return:
    """
    from plugins.windows.sysinfo import Win32Info
    info = Win32Info()
    return info.collect

