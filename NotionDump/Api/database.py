# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import logging
import shutil
import os
from notion_client import Client
from notion_client import AsyncClient
from notion_client import APIErrorCode, APIResponseError
import json
from json import JSONDecodeError
import NotionDump
from NotionDump.Parser.database_parser import DatabaseParser


class Database:
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
        self.database_parser = DatabaseParser(self.database_id)

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    # 获取到所有的数据库数据(JSon格式)
    def query_database(self, db_q_filter="{}", db_q_sorts="[]"):
        query_ret = "{}"
        # 组合查询条件
        query_post = {"database_id": self.database_id}
        if db_q_sorts != "[]":
            query_post["sorts"] = db_q_sorts
        if db_q_filter != "{}":
            query_post["filter"] = db_q_sorts
        try:
            query_ret = self.client.databases.query(
                **query_post
            )

            # 大量数据一次未读完（未测试）
            next_cur = query_ret["next_cursor"]
            while query_ret["has_more"]:
                query_post["start_cursor"] = next_cur
                db_query_ret = self.client.databases.query(
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

    # 获取数据库信息
    def retrieve_database(self):
        try:
            return self.client.databases.retrieve(database_id=self.database_id)
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                logging.exception("Database is invalid")
            else:
                # Other error handling code
                logging.exception(error)

        return None

    # 获取到所有的数据库数据(CSV格式)(数据库导出均是CSV)
    def database_to_csv(self, csv_name=None, col_name_list=None, db_q_filter="{}", db_q_sorts="[]"):
        db_json = self.query_database(db_q_filter=db_q_filter, db_q_sorts=db_q_sorts)
        if db_json is None:
            return False

        tmp_csv_filename = self.database_parser.database_to_csv(db_json, col_name_list)
        if csv_name is not None:
            shutil.copyfile(tmp_csv_filename, csv_name)
        return True

    def database_to_db(self, col_name_list=None, db_q_filter="{}", db_q_sorts="[]"):
        # 从配置文件中获取数据库配置，打开数据库，并将csv文件写入到数据库中
        db_json = self.query_database(db_q_filter=db_q_filter, db_q_sorts=db_q_sorts)
        if db_json is None:
            return None

        tmp_csv_filename = self.database_parser.database_to_csv(db_json, col_name_list)
        # TODO
        # 将CSV文件写入到数据库
        # 调用SQL中的notion2sql提供的接口
        return

    # 源文件，直接输出成json
    def database_to_json(self, json_name=None, db_q_filter="{}", db_q_sorts="[]"):
        db_json = self.query_database(db_q_filter=db_q_filter, db_q_sorts=db_q_sorts)
        if db_json is None:
            return None
        json_handle = None
        try:
            json_handle = json.dumps(db_json, ensure_ascii=False, indent=4)
        except JSONDecodeError:
            print("json decode error")
            return

        if json_name is None:
            json_name = self.tmp_dir + self.database_id + ".json"
        file = open(json_name, "w+", encoding="utf-8")
        file.write(json_handle)
        return
