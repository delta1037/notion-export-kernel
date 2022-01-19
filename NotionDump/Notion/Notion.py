# author: delta1037
# Date: 2022/01/10
# mail:geniusrabbit@qq.com
import os
from time import sleep

from notion_client import Client, AsyncClient
from notion_client import APIErrorCode, APIResponseError

import NotionDump
from NotionDump.utils import common_op, internal_var


class NotionQuery:
    def __init__(self, token, client_handle=None, async_api=False):
        self.token = token
        if client_handle is None and token is not None:
            # 有的token话就初始化一下
            if not async_api:
                self.client = Client(auth=self.token)
            else:
                self.client = AsyncClient(auth=self.token)
        else:
            # 没有token，传进来handle就用，没传就不用
            self.client = client_handle

        if self.client is None:
            common_op.debug_log("notion query init fail", level=NotionDump.DUMP_MODE_DEFAULT)

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        self.friendly_time = internal_var.FRIENDLY_USE_API

    def __friendly_use_api(self):
        sleep(self.friendly_time / 1000)

    # 获取该块下所有的子块
    def retrieve_block_children(self, block_id, page_size=50):
        self.__friendly_use_api()
        query_post = {
            "block_id": block_id,
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
            if NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEBUG:
                self.__save_to_json(query_ret, block_id, prefix="retrieve_")
            return query_ret
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                common_op.debug_log("Block " + block_id + " Retrieve child is invalid",
                                    level=NotionDump.DUMP_MODE_DEFAULT)
            else:
                # Other error handling code
                common_op.debug_log(error)
                common_op.debug_log("Block " + block_id + " response error", level=NotionDump.DUMP_MODE_DEFAULT)
        except Exception as e:
            common_op.debug_log(e)
            common_op.debug_log("Block " + block_id + " Not found or no authority", level=NotionDump.DUMP_MODE_DEFAULT)
        return None

    # 获取到所有的数据库数据(JSon格式)
    def query_database(self, database_id, db_q_filter="{}", db_q_sorts="[]"):
        self.__friendly_use_api()
        # 组合查询条件
        query_post = {"database_id": database_id}
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
                # TODO 这里还没有将内容搞出来
                next_cur = db_query_ret["next_cursor"]
            if NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEBUG:
                self.__save_to_json(query_ret, database_id, prefix="query_")
            return query_ret
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                common_op.debug_log("Database Query is invalid, id=" + database_id,
                                    level=NotionDump.DUMP_MODE_DEFAULT)
            else:
                # Other error handling code
                common_op.debug_log(error)
                common_op.debug_log("Database Query is invalid, id=" + database_id, level=NotionDump.DUMP_MODE_DEFAULT)
        except Exception as e:
            common_op.debug_log(e)
            common_op.debug_log("Database Query Not found or no authority, id=" + database_id, level=NotionDump.DUMP_MODE_DEFAULT)
        return None

    # 获取数据库信息
    def retrieve_database(self, database_id):
        self.__friendly_use_api()
        try:
            retrieve_ret = self.client.databases.retrieve(database_id=database_id)
            if NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEBUG:
                self.__save_to_json(retrieve_ret, database_id, prefix="retrieve_")
            return retrieve_ret
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                common_op.debug_log("Database retrieve is invalid, id=" + database_id,
                                    level=NotionDump.DUMP_MODE_DEFAULT)
            else:
                # Other error handling code
                common_op.debug_log(error)
                common_op.debug_log("Database retrieve is invalid, id=" + database_id, level=NotionDump.DUMP_MODE_DEFAULT)
        except Exception as e:
            common_op.debug_log(e)
            common_op.debug_log("Database retrieve Not found or no authority, id=" + database_id,
                                level=NotionDump.DUMP_MODE_DEFAULT)
        return None

    # 获取Page的信息
    def retrieve_page(self, page_id):
        self.__friendly_use_api()
        try:
            retrieve_ret = self.client.pages.retrieve(page_id=page_id)
            if NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEBUG:
                self.__save_to_json(retrieve_ret, page_id, prefix="retrieve_")
            return retrieve_ret
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                common_op.debug_log("Page retrieve is invalid, id=" + page_id,
                                    level=NotionDump.DUMP_MODE_DEFAULT)
            else:
                # Other error handling code
                common_op.debug_log(error)
                common_op.debug_log("Page retrieve is invalid, id=" + page_id,
                                    level=NotionDump.DUMP_MODE_DEFAULT)
        except Exception as e:
            common_op.debug_log(e)
            common_op.debug_log("Page retrieve Not found or no authority, id=" + page_id,
                                level=NotionDump.DUMP_MODE_DEFAULT)
        return None

    # 源文件，直接输出成json; 辅助测试使用
    def __save_to_json(self, page_json, json_id, json_name=None, prefix=None):
        if json_name is None:
            if prefix is not None:
                json_name = self.tmp_dir + prefix + json_id + ".json"
            else:
                json_name = self.tmp_dir + json_id + ".json"
        common_op.save_json_to_file(page_json, json_name)
