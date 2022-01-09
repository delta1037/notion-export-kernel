# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import json
import logging
import shutil
from json import JSONDecodeError

from notion_client import Client
from notion_client import AsyncClient
from notion_client import APIErrorCode, APIResponseError
import os

import NotionDump
from NotionDump.Parser.page_parser import PageParser


class Page:
    # 初始化
    def __init__(self, token, page_id, client_handle=None, async_api=False):
        self.token = token
        self.page_id = page_id
        if client_handle is None:
            if not async_api:
                self.client = Client(auth=self.token)
            else:
                self.client = AsyncClient(auth=self.token)
        else:
            self.client = client_handle
        self.page_parser = PageParser(self.page_id, parser_type=NotionDump.PARSER_TYPE_MD)
        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    # 获取Page的信息
    def retrieve_page(self):
        try:
            return self.client.pages.retrieve(page_id=self.page_id)
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                logging.exception("Database is invalid")
            else:
                # Other error handling code
                logging.exception(error)
        return None

    # 获取Page的所有块
    def query_page(self, page_size=50):
        query_post = {
            "block_id": self.page_id,
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
                logging.exception("Database is invalid")
            else:
                # Other error handling code
                logging.exception(error)
        return None

    # 获取到所有的PAGE数据
    def page_to_md(self, md_name=None):
        page_json = self.query_page()
        if page_json is None:
            return False

        tmp_csv_filename = self.page_parser.page_to_md(page_json)
        if md_name is not None:
            shutil.copyfile(tmp_csv_filename, md_name)
        return True

    def page_to_db(self):
        # 从配置文件中获取数据库配置，打开数据库，并将csv文件写入到数据库中
        page_json = self.query_page()
        if page_json is None:
            return None

        # tmp_csv_filename = self.database_parser.database_to_csv(db_json, col_name_list)
        # TODO
        # 将CSV文件写入到数据库
        # 调用SQL中的notion2sql提供的接口
        return

    # 源文件，直接输出成json
    def page_to_json(self, json_name=None):
        page_json = self.query_page()
        if page_json is None:
            return None
        json_handle = None
        try:
            json_handle = json.dumps(page_json, ensure_ascii=False, indent=4)
        except JSONDecodeError:
            print("json decode error")
            return

        if json_name is None:
            json_name = self.tmp_dir + self.page_id + ".json"
        file = open(json_name, "w+", encoding="utf-8")
        file.write(json_handle)
        return
