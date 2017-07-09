# -*- coding:utf-8 -*-
# @Time     : 2017-06-29 17:49
# @Author   : gck1d6o
# @Site     : 
# @File     : HouseStark.py
# @Software : PyCharm
import requests
import sys
import os
import json
from datetime import datetime
from pprint import pprint

# 自定义模块
from conf import settings
from core import info_collection
from core import api_token


class ArgvHandler(object):
    """
    核心功能实现类，接收run.py传递过来的参数。
    """
    def __init__(self, argv_list):
        self.argv = argv_list
        self.parse_argv()
        self.asset_id_file = None

    def parse_argv(self):
        if len(self.argv) > 1:
            if hasattr(self, self.argv[1]):
                func = getattr(self, self.argv[1])
                func()
            else:
                self.help_msg()
        else:
            self.help_msg()

    @staticmethod
    def help_msg():
        msg = """
        collect_data   收集资产信息
        run_forever
        get_asset_id
        report_asset   收集资产信息并汇报给CMDB
        """
        print(msg)

    @staticmethod
    def collect_data():
        """
        收集资产信息
        """
        obj = info_collection.InfoCollection()
        asset_data = obj.collect()
        pprint(asset_data)

    def run_forever(self):
        pass

    def get_asset_id(self):
        pass

    def report_asset(self):
        """
        向CMDB Server报告资产信息
        """
        obj = info_collection.InfoCollection()
        asset_data = obj.collect()
        asset_id = self.load_asset_id()
        if asset_id is not None:
            asset_data["asset_id"] = asset_id
            url = "asset_report"
        else:
            asset_data["asset_id"] = None
            url = "asset_report_with_no_id"
        data = {"asset_data": json.dumps(asset_data)}
        response = self.submit_data(url, data, method="post")
        if "asset_id" in response:
            print("==================>>>>>", response)
            """如果CMDB返回了该资产的asset_id就存在到本地var目录中"""
            self.update_asset_id(response["asset_id"])
        self.log_record(response)

    def load_asset_id(self):
        """获取asset_id并返回，如果获取不到默认返回None"""
        self.asset_id_file = settings.Params["asset_id"]
        if os.path.isfile(self.asset_id_file):
            asset_id = open(self.asset_id_file).read().strip()
            return asset_id

    def submit_data(self, port_url, data, method="post"):
        """
        向CMDB Server POST提交收集到的资产信息
        :param port_url: 根据asset_id是否存在调用不同的URL
        :param data:   收集到的资产信息
        :param method: 一直使用post进行提交
        :return:
        """
        if port_url in settings.Params["urls"]:
            url_str = "http://%s:%s%s" % (settings.Params["server"],
                                          settings.Params["port"],
                                          settings.Params["urls"][port_url])
            """启用api_token认证"""
            url = self.attach_token(url_str)
            if method == "get":
                """一直没有用到get方法"""
                args = ""
                for k, v in data.items():
                    args += "&%s=%s" % (k, v)
                args = args[1:]
                url_with_args = "%s?%s" % (url, args)
                try:
                    req = requests.get(url_with_args)
                    callback = req.text
                    print("=====================>>>", req)
                    return callback
                except requests.RequestException as e:
                    sys.exit(e)
            elif method == "post":
                """资产新建和资产更新都使用post方法"""
                try:
                    req = requests.post(url, data=data)
                    callback = json.loads(req.text)
                    print("=====================>>>", req.text)
                    return callback
                except requests.RequestException as e:
                    sys.exit(e)
        else:
            raise KeyError

    def update_asset_id(self, asset_id):
        """接收asset_id并到var目录中"""
        with open(self.asset_id_file, "w") as f:
            f.write(str(asset_id))

    def log_record(self, log):
        """记录资产更新的日志"""
        if type(log) is dict:
            log_file = settings.Params["log_file"]
            with open(log_file, "a") as f:
                if "info" in log:
                    for msg in log["info"]:
                        f.write(self.log_format("info", msg))
                elif "error" in log:
                    for msg in log["error"]:
                        f.write(self.log_format("error", msg))
                elif "warning" in log:
                    for msg in log["warning"]:
                        f.write(self.log_format("warning", msg))
                else:
                    for msg in log:
                        f.write(self.log_format(msg=msg))

    @staticmethod
    def log_format(level="info", msg=None):
        """格式化日志"""
        return "%s\t%s\T%s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, msg)

    @staticmethod
    def attach_token(url_str):
        user = settings.Params["auth"]["user"]
        token_id = settings.Params["auth"]["token"]
        md5_token, timestamp = api_token.get_token(user, token_id)
        url_arg_str = "user=%s&timestamp=%s&token=%s" % (user, timestamp, md5_token)
        if "?" in url_str:
            new_url = url_str + "&" + url_arg_str
        else:
            new_url = url_str + "?" + url_arg_str
        return new_url


if __name__ == '__main__':
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
