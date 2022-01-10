# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

import os
import logging
import shutil

import NotionDump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.Parser.page_parser import PageParser
from NotionDump.Parser.database_parser import DatabaseParser
from NotionDump.utils import common_op


class Database:
    # 初始化
    def __init__(self, database_id, query_handle: NotionQuery, export_child_pages=False):
        self.database_id = database_id.replace('-', '')
        self.query_handle = query_handle

        # 数据库解析并不需要传额外的信息
        self.database_parser = DatabaseParser(self.database_id)

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        # 是否导出子页面
        self.export_child_page = export_child_pages

    def get_child_pages_dic(self):
        return self.database_parser.get_child_page_dic()

    # 获取到所有的数据库数据(CSV格式)(数据库导出均是CSV)
    def database_to_csv(self, csv_name=None, col_name_list=None, db_q_filter="{}", db_q_sorts="[]"):
        db_json = self.query_handle.query_database(
            database_id=self.database_id,
            db_q_filter=db_q_filter,
            db_q_sorts=db_q_sorts)
        if db_json is None:
            return ""

        tmp_csv_filename = self.database_parser.database_to_csv(db_json, col_name_list)
        if csv_name is not None:
            shutil.copyfile(tmp_csv_filename, csv_name)
            return csv_name
        return tmp_csv_filename

    def database_to_db(self, col_name_list=None, db_q_filter="{}", db_q_sorts="[]"):
        # 从配置文件中获取数据库配置，打开数据库，并将csv文件写入到数据库中
        db_json = self.query_handle.query_database(
            database_id=self.database_id,
            db_q_filter=db_q_filter,
            db_q_sorts=db_q_sorts)
        if db_json is None:
            return ""

        tmp_csv_filename = self.database_parser.database_to_csv(db_json, col_name_list)
        # TODO 将CSV文件写入到数据库；调用SQL中的notion2sql提供的接口
        return tmp_csv_filename

    # 源文件，直接输出成json; 辅助测试使用
    def database_to_json(self, json_name=None, db_q_filter="{}", db_q_sorts="[]"):
        db_json = self.query_handle.query_database(
            database_id=self.database_id,
            db_q_filter=db_q_filter,
            db_q_sorts=db_q_sorts)
        if db_json is None:
            return ""

        if json_name is None:
            json_name = self.tmp_dir + self.database_id + ".json"
        common_op.save_json_to_file(db_json, json_name)
