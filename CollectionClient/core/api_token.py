# -*- coding:utf-8 -*-
# @Time     : 2017-07-07 11:22
# @Author   : gck1d6o
# @Site     : 
# @File     : api_token.py
# @Software : PyCharm

import hashlib
import time


def get_token(username, token_id):
    """
    根据用户名+约定的token_id+时间戳 生成md5,然后截取10-20位的字符串，
    并将 截取的md5值和时间戳一起发给CMDB Server进行验证。
    """
    timestamp = int(time.time())
    md5_format_str = "%s\n%s\n%s" % (username, timestamp, token_id)
    md5_token = hashlib.md5()
    md5_token.update(md5_format_str.encode("utf-8"))
    return md5_token.hexdigest()[10:20], timestamp


if __name__ == '__main__':
    get_token("rick", "test")
