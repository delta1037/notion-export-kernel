# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

import os
import logging

from notion_client import Client, AsyncClient
from notion_client import APIErrorCode, APIResponseError

import NotionDump
from NotionDump.utils import common_op


# Block内容解析
class Block:
    # 初始化
    def __init__(self, block_id, token, client_handle=None, async_api=False):
        self.token = token
        self.block_id = block_id.replace('-', '')
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

    # 获取该块下所有的子块
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

            if NotionDump.DUMP_DEBUG or export_json:
                # 调试时输出所有的子页面
                self.block_to_json(query_ret)
            return query_ret
        except APIResponseError as error:
            if NotionDump.DUMP_DEBUG:
                if error.code == APIErrorCode.ObjectNotFound:
                    logging.exception("Block " + self.block_id + " Retrieve child is invalid")
                else:
                    # Other error handling code
                    logging.exception(error)
            else:
                logging.exception("Block " + self.block_id + " Retrieve child is invalid")
        except Exception as e:
            if NotionDump.DUMP_DEBUG:
                logging.exception(e)
            else:
                logging.exception("Block " + self.block_id + " Not found or no authority")
        return None

    # 源文件，直接输出成json; 辅助测试使用
    def block_to_json(self, block_json, json_name=None):
        if block_json is None:
            return None

        if json_name is None:
            json_name = self.tmp_dir + self.block_id + ".json"
        common_op.save_json_to_file(block_json, json_name)
