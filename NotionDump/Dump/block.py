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
    def __init__(self, block_id):
        self.block_id = block_id.replace('-', '')

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    # 源文件，直接输出成json; 辅助测试使用
    def block_to_json(self, block_json, json_name=None):
        if block_json is None:
            return None

        if json_name is None:
            json_name = self.tmp_dir + self.block_id + ".json"
        common_op.save_json_to_file(block_json, json_name)
