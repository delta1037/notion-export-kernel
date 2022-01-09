# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import logging
from notion_client import Client
from notion_client import AsyncClient
from notion_client import APIErrorCode, APIResponseError
import json
from json import JSONDecodeError


# Block内容解析
class Block:
    # 初始化
    def __init__(self, token, database_id, client_handle=None, async_api=False):
        self.token = token
        self.database_id = database_id
        if client_handle is None:
            if not async_api:
                self.client = Client(auth=self.token)
            else:
                self.client = AsyncClient(auth=self.token)
        else:
            self.client = client_handle



