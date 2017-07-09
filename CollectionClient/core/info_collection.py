# -*- coding:utf-8 -*-
# @Time     : 2017-06-30 11:06
# @Author   : gck1d6o
# @Site     : 
# @File     : info_collection.py
# @Software : PyCharm

import sys
import platform
from pprint import pprint

from plugins import plugin_api


class InfoCollection(object):
    """
    信息收集
    """
    def __init__(self):
        pass

    @staticmethod
    def get_platform():
        """
        :return: 操作系统平台
        """
        return platform.system()

    def collect(self):
        os_platform = self.get_platform()
        try:
            func = getattr(self, os_platform.lower())
            info_data = func()
            return self.build_report_data(info_data)
        except AttributeError as e:
            sys.exit("OS Error: The Client can't support os [%s]!" % os_platform)

    @staticmethod
    def build_report_data(data):
        """
        add csrf token info to data
        :param data: 原始数据
        :return: 封装后的数据
        """
        return data

    @staticmethod
    def linux():
        """
        linux收集系统信息接口
        :return:
        """
        return plugin_api.linux_sys_info()

    @staticmethod
    def windows():
        """
        windows收集系统信息接口
        :return:
        """
        return plugin_api.windows_sys_info()


if __name__ == '__main__':
    info = InfoCollection()
    pprint(info.collect())