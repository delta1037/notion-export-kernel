# author: delta1037
# Date: 2022/01/10
# mail:geniusrabbit@qq.com
import logging

import NotionDump
from notion_client import Client, AsyncClient
from notion_client import APIErrorCode, APIResponseError


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
            logging.exception("notion query init fail")

    # 获取该块下所有的子块
    def retrieve_block_children(self, block_id, page_size=50):
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
            return query_ret
        except APIResponseError as error:
            if NotionDump.DUMP_DEBUG:
                if error.code == APIErrorCode.ObjectNotFound:
                    logging.exception("Block " + block_id + " Retrieve child is invalid")
                else:
                    # Other error handling code
                    logging.exception(error)
            else:
                logging.exception("Block " + block_id + " Retrieve child is invalid")
        except Exception as e:
            if NotionDump.DUMP_DEBUG:
                logging.exception(e)
            else:
                logging.exception("Block " + block_id + " Not found or no authority")
        return None

    # 获取到所有的数据库数据(JSon格式)
    def query_database(self, database_id, db_q_filter="{}", db_q_sorts="[]"):
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
                next_cur = db_query_ret["next_cursor"]
            return query_ret
        except APIResponseError as error:
            if NotionDump.DUMP_DEBUG:
                if error.code == APIErrorCode.ObjectNotFound:
                    logging.exception("Database Query is invalid, id=" + database_id)
                else:
                    # Other error handling code
                    logging.exception(error)
            else:
                logging.exception("Database Query is invalid, id=" + database_id)
        except Exception as e:
            if NotionDump.DUMP_DEBUG:
                logging.exception(e)
            else:
                logging.exception("Database Query Not found or no authority, id=" + database_id)
        return None

    # 获取数据库信息
    def retrieve_database(self, database_id):
        try:
            return self.client.databases.retrieve(database_id=database_id)
        except APIResponseError as error:
            if NotionDump.DUMP_DEBUG:
                if error.code == APIErrorCode.ObjectNotFound:
                    logging.exception("Database Retrieve is invalid, id=" + database_id)
                else:
                    # Other error handling code
                    logging.exception(error)
            else:
                logging.exception("Database Retrieve is invalid, id=" + database_id)
        except Exception as e:
            if NotionDump.DUMP_DEBUG:
                logging.exception(e)
            else:
                logging.exception("Database Retrieve Not found or no authority, id=" + database_id)
        return None

    # 获取Page的信息
    def retrieve_page(self, page_id):
        try:
            return self.client.pages.retrieve(page_id=page_id)
        except APIResponseError as error:
            if NotionDump.DUMP_DEBUG:
                if error.code == APIErrorCode.ObjectNotFound:
                    logging.exception("Page Retrieve is invalid, id=" + page_id)
                else:
                    # Other error handling code
                    logging.exception(error)
            else:
                logging.exception("Page Retrieve is invalid, id=" + page_id)
        except Exception as e:
            if NotionDump.DUMP_DEBUG:
                logging.exception(e)
            else:
                logging.exception("Page Retrieve Not found or no authority, id=" + page_id)
        return None
