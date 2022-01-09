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
    def __init__(self, block_id, token, client_handle=None, async_api=False):
        self.token = token
        self.block_id = block_id
        if client_handle is None:
            if not async_api:
                self.client = Client(auth=self.token)
            else:
                self.client = AsyncClient(auth=self.token)
        else:
            self.client = client_handle

    # 获取该块下所有的子块，对于
    def retrieve_block_children(self, page_size=50):
        query_post = {
            "block_id": self.block_id,
            "page_size": page_size
        }
        try:
            query_ret = self.client.blocks.children.list(
                **query_post
            )

            # 大量数据一次未读完（未测试）
            next_cur = query_ret["next_cursor"]
            while query_ret["has_more"]:
                query_post["start_cursor"] = next_cur
                db_query_ret = self.client.blocks.children.list(
                    **query_post
                )
                next_cur = db_query_ret["next_cursor"]
            return query_ret
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                logging.exception("Block " + self.block_id + " is invalid")
            else:
                # Other error handling code
                logging.exception(error)
        return None



