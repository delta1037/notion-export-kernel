# author: delta1037
# Date: 2022/01/10
# mail:geniusrabbit@qq.com
import os
from time import sleep, time
import urllib.request
from time import time, sleep
from urllib.error import URLError
from urllib.parse import quote
from notion_client import Client, AsyncClient
from notion_client import APIErrorCode, APIResponseError

import NotionDump
from NotionDump.Notion.Buffer import Buffer
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

        self.last_call_time = None
        self.friendly_time = internal_var.FRIENDLY_USE_API

        self.buffer = Buffer()

    def safe_save(self):
        self.buffer.save_buffer()

    def __friendly_use_api(self):
        now_time = time()
        # 睡眠时间 = 间隔时间 - 函数执行时间
        if self.last_call_time is None:
            func_exec_ms = self.friendly_time
        else:
            func_exec_ms = int(round(now_time * 1000)) - int(round(self.last_call_time * 1000))
        sleep_ms = self.friendly_time - func_exec_ms
        while sleep_ms > 0:
            # 如果需要睡眠
            if sleep_ms > 100:
                sleep(0.1)
            else:
                sleep(sleep_ms / 1000.0)
            # 按照每次100ms累计
            common_op.debug_log("wait for server response..." + str(sleep_ms) + "ms", level=NotionDump.DUMP_MODE_DEFAULT)
            sleep_ms -= 100
        # 更新上次执行时间
        self.last_call_time = time()

    # 获取该块下所有的子块
    def retrieve_block_children(self, block_id, parent_id=None, page_size=100):
        # 添加缓存系统
        if NotionDump.USE_BUFFER:
            if parent_id is not None:
                dirty = self.buffer.select_buffer(parent_id, is_child=True)
            else:
                dirty = self.buffer.select_buffer(block_id)
            if not dirty:
                # 缓存命中，直接从缓存中加载数据
                common_op.debug_log("[##CACHE] cached and load " + block_id + ";parent is " + str(parent_id), level=NotionDump.DUMP_MODE_DEFAULT)
                load = self.__load_from_json(block_id, prefix="retrieve_block_")
                if load is not None:
                    return load

        common_op.debug_log("[&&CACHE] no cached and load " + block_id + ";parent is " + str(parent_id), level=NotionDump.DUMP_MODE_DEFAULT)
        self.__friendly_use_api()
        query_post = {
            "block_id": block_id,
            "page_size": page_size
        }
        try:
            query_ret = self.client.blocks.children.list(
                **query_post
            )

            # 大量数据一次未读完
            next_cur = query_ret["next_cursor"]
            while query_ret["has_more"]:
                query_post["start_cursor"] = next_cur
                common_op.debug_log(query_post, level=NotionDump.DUMP_MODE_DEFAULT)
                db_query_ret = self.client.blocks.children.list(
                    **query_post
                )
                next_cur = db_query_ret["next_cursor"]
                query_ret["results"] += db_query_ret["results"]
                if next_cur is None:
                    break
            if NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEBUG or NotionDump.USE_BUFFER:
                self.__save_to_json(query_ret, block_id, prefix="retrieve_block_")
            if NotionDump.USE_BUFFER and parent_id is None:
                # 独立的page 更新页面状态
                self.buffer.update_buffer(block_id)
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
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("Block " + block_id + " Not found or no authority", level=NotionDump.DUMP_MODE_DEFAULT)
        return None

    # 获取到所有的数据库数据(JSon格式)
    def query_database(self, database_id, db_q_filter="{}", db_q_sorts="[]"):
        # 添加缓存系统
        if NotionDump.USE_BUFFER:
            if not self.buffer.select_buffer(database_id):
                # 缓存命中，直接从缓存中加载数据
                common_op.debug_log("[##CACHE] cached and load " + database_id, level=NotionDump.DUMP_MODE_DEFAULT)
                load = self.__load_from_json(database_id, prefix="query_db_")
                if load is not None:
                    return load
        common_op.debug_log("[&&CACHE] no cached and load " + database_id, level=NotionDump.DUMP_MODE_DEFAULT)

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

            # 大量数据一次未读完
            next_cur = query_ret["next_cursor"]
            while query_ret["has_more"]:
                query_post["start_cursor"] = next_cur
                common_op.debug_log(query_post, level=NotionDump.DUMP_MODE_DEFAULT)
                db_query_ret = self.client.databases.query(
                    **query_post
                )
                next_cur = db_query_ret["next_cursor"]
                query_ret["results"] += db_query_ret["results"]
                if next_cur is None:
                    break

            if NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEBUG or NotionDump.USE_BUFFER:
                self.__save_to_json(query_ret, database_id, prefix="query_db_")
            if NotionDump.USE_BUFFER:
                # 独立的page 更新页面状态
                self.buffer.update_buffer(database_id)
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
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("Database Query Not found or no authority, id=" + database_id, level=NotionDump.DUMP_MODE_DEFAULT)
        return None

    # 获取数据库信息
    def retrieve_database(self, database_id):
        self.__friendly_use_api()
        try:
            retrieve_ret = self.client.databases.retrieve(database_id=database_id)
            if NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEBUG or NotionDump.USE_BUFFER:
                self.__save_to_json(retrieve_ret, database_id, prefix="retrieve_db_")
            if NotionDump.USE_BUFFER and retrieve_ret is not None and "last_edited_time" in retrieve_ret:
                self.buffer.add_buffer(database_id, retrieve_ret["last_edited_time"], id_type="database")
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
            if NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEBUG or NotionDump.USE_BUFFER:
                self.__save_to_json(retrieve_ret, page_id, prefix="retrieve_page_")
            if NotionDump.USE_BUFFER and retrieve_ret is not None and "last_edited_time" in retrieve_ret:
                self.buffer.add_buffer(page_id, retrieve_ret["last_edited_time"])
            return retrieve_ret
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                common_op.debug_log("Page retrieve is invalid(api), id=" + page_id,
                                    level=NotionDump.DUMP_MODE_DEFAULT)
            else:
                # Other error handling code
                common_op.debug_log(error)
                common_op.debug_log("Page retrieve is invalid(other), id=" + page_id,
                                    level=NotionDump.DUMP_MODE_DEFAULT)
        except Exception as e:
            common_op.debug_log(e)
            common_op.debug_log("Page retrieve Not found or no authority, id=" + page_id,
                                level=NotionDump.DUMP_MODE_DEFAULT)
        return None

    def download_to_file(self, download_id, child_page_item):
        # 设置文件链接嵌入时，只有存储在Notion的文件需要下载（不下载会由于时间问题导致链接失效）
        if NotionDump.FILE_WITH_LINK and "secure.notion-static.com" not in child_page_item["link_src"]:
            return ""

        # 解析文件后缀名
        file_url = child_page_item["link_src"]
        common_op.debug_log("download url is " + file_url, level=NotionDump.DUMP_MODE_DEBUG)
        if file_url == "":
            return ""
        # 文件名在最后一个/和?之间
        if file_url.find('?') != -1:
            filename = file_url[file_url.rfind('/') + 1:file_url.find('?')]
        else:
            filename = file_url[file_url.rfind('/') + 1:]
        file_suffix = filename[filename.find('.'):]
        # 使用后缀和id生成可识别的文件
        download_name = self.tmp_dir + download_id + file_suffix
        common_op.debug_log("download name " + download_name, level=NotionDump.DUMP_MODE_DEBUG)

        if NotionDump.USE_BUFFER:
            # 看文件是否需要重新下载
            if not self.buffer.select_buffer(download_id) and os.path.exists(download_name):
                return download_name

            # 新增记录（注意这里与上面select不属于同一个执行分支）
            self.buffer.add_buffer(download_id, "", id_type="file")

        if os.path.exists(download_name):
            common_op.debug_log("[WARN] file " + download_name + " was covered", level=NotionDump.DUMP_MODE_DEFAULT)
        # 下载文件
        self.__friendly_use_api()
        try:
            file_url = quote(file_url, safe='/:?=&%')
            urllib.request.urlretrieve(file_url, download_name)
            if NotionDump.USE_BUFFER:
                self.buffer.update_buffer(download_id)
            return download_name
        except urllib.error.HTTPError as e:
            common_op.debug_log("download name " + download_name + " get error:HTTPError",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:HTTPError",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        except urllib.error.ContentTooShortError as e:
            common_op.debug_log("download name " + download_name + " get error:ContentTooShortError",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:ContentTooShortError",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        except urllib.error.URLError as e:
            common_op.debug_log("download name " + download_name + " get error:URLError",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:URLError",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        except TimeoutError as e:
            common_op.debug_log("download name " + download_name + " get error:TimeoutError",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:TimeoutError",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        except Exception as e:
            common_op.debug_log("download name " + download_name + " get error:Exception",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:Exception",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        return ""

    # 源文件，直接输出成json; 辅助测试使用
    def __save_to_json(self, page_json, json_id, json_name=None, prefix=None):
        if json_name is None:
            if prefix is not None:
                json_name = self.tmp_dir + prefix + json_id + ".json"
            else:
                json_name = self.tmp_dir + json_id + ".json"
        common_op.save_json_to_file(page_json, json_name)

    def __load_from_json(self, json_id, json_name=None, prefix=None):
        if json_name is None:
            if prefix is not None:
                json_name = self.tmp_dir + prefix + json_id + ".json"
            else:
                json_name = self.tmp_dir + json_id + ".json"
        return common_op.load_json_from_file(json_name)
