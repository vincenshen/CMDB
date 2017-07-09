# -*- coding:utf-8 -*-
# @Time     : 2017-07-07 14:15
# @Author   : gck1d6o
# @Site     : 
# @File     : api_token.py
# @Software : PyCharm

import hashlib
import json

from django.shortcuts import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from Asset import models


def gen_token(username, timestamp, token_id):
    token_format = "%s\n%s\n%s" % (username, timestamp, token_id)
    token_obj = hashlib.md5()
    token_obj.update(token_format.encode())
    return token_obj.hexdigest()[10:20]


def token_required(func):
    def wrapper(*args, **kwargs):
        response = {"error": []}
        get_args = args[0].GET
        username = get_args.get("user", "")
        token_md5_from_client = get_args.get("token", "")
        timestamp = get_args.get("timestamp", "")

        if all([username, token_md5_from_client, timestamp]):
            try:
                user_obj = models.UserProfile.objects.get(username=username)
                token_md5_from_server = gen_token(username, timestamp, user_obj.token_id)
                if token_md5_from_client == token_md5_from_server:
                    print("\033[31;1mPass authentication\033[0m")
                else:
                    response["error"].append({"auth_failed": "Invalid username or token_id"})
                    print("\033[31;1mfailed authentication\033[0m")
            except ObjectDoesNotExist as e:
                response['errors'].append({"auth_failed": "Invalid username or token_id"})
        else:
            response['errors'].append({"auth_failed": "This api requires token authentication!"})

        if response["error"]:
            return HttpResponse(json.dumps(response))
        return func(*args, **kwargs)
    return wrapper
