# -*- coding:utf-8 -*-
# @Time     : 2017-06-30 16:22
# @Author   : gck1d6o
# @Site     : 
# @File     : settings.py
# @Software : PyCharm

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Params = {
    "server": "127.0.0.1",
    "port": 8000,
    "request_timeout": 30,
    "urls": {
        "asset_report_with_no_id": "/report/asset_with_no_asset_id/",
        "asset_report": "/report/"
    },
    "asset_id": "%s/var/.asset_id" % BASE_DIR,
    "log_file": "%s/logs/run_log" % BASE_DIR,
    "auth": {
        "user": "admin",
        "token": "admin123",
    },
}
