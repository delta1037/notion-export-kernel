# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import logging
from notion_client import Client
from notion_client import AsyncClient
from notion_client import APIErrorCode, APIResponseError
import json
from json import JSONDecodeError
import NotionDump
import os


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

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    # 获取该块下所有的子块，对于
    def retrieve_block_children(self, page_size=50, export_json=False):
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

            if export_json:
                self.block_to_json(query_ret)
            return query_ret
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                logging.exception("Block " + self.block_id + " is invalid")
            else:
                # Other error handling code
                logging.exception(error)
        return None

    # 导出内容到json文件中
    def block_to_json(self, block_json, json_name=None):
        if block_json is None:
            return None
        json_handle = None
        try:
            json_handle = json.dumps(block_json, ensure_ascii=False, indent=4)
        except JSONDecodeError:
            print("json decode error")
            return

        if json_name is None:
            json_name = self.tmp_dir + self.block_id + ".json"
        file = open(json_name, "w+", encoding="utf-8")
        file.write(json_handle)
        return

