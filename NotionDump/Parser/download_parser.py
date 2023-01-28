# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

import os
import urllib.request
from time import time, sleep
from urllib.error import URLError
from urllib.parse import quote

import NotionDump
from NotionDump.utils import common_op, internal_var


class DownloadParser:
    def __init__(self, download_id):
        self.download_id = download_id

        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        self.last_call_time = None
        self.friendly_time = internal_var.FRIENDLY_DOWNLOAD

    def download_to_file(self, new_id, child_page_item):
        # 设置文件链接嵌入时，只有存储在Notion的文件需要下载（不下载会由于时间问题导致链接失效）
        if NotionDump.FILE_WITH_LINK and "secure.notion-static.com" not in child_page_item["link_src"]:
            return ""
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
            common_op.debug_log("wait for server response..." + str(sleep_ms) + "ms",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            sleep_ms -= 100
        # 更新上次执行时间
        self.last_call_time = time()

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
        download_name = self.tmp_dir + new_id + file_suffix
        if os.path.exists(download_name):
            common_op.debug_log("[WARN] file " + download_name + " was covered", level=NotionDump.DUMP_MODE_DEFAULT)
        common_op.debug_log("download name " + download_name, level=NotionDump.DUMP_MODE_DEBUG)
        # 下载文件
        try:
            file_url = quote(file_url, safe='/:?=&%')
            urllib.request.urlretrieve(file_url, download_name)
            return download_name
        except urllib.error.HTTPError as e:
            common_op.debug_log("download name " + download_name + " get error:HTTPError", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:HTTPError", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        except urllib.error.ContentTooShortError as e:
            common_op.debug_log("download name " + download_name + " get error:ContentTooShortError", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:ContentTooShortError", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        except urllib.error.URLError as e:
            common_op.debug_log("download name " + download_name + " get error:URLError", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:URLError", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        except TimeoutError as e:
            common_op.debug_log("download name " + download_name + " get error:TimeoutError", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:TimeoutError", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        except Exception as e:
            common_op.debug_log("download name " + download_name + " get error:Exception", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log("download url " + file_url + " get error:Exception", level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(e, level=NotionDump.DUMP_MODE_DEFAULT)
        return ""

# https://s3.us-west-2.amazonaws.com/secure.notion-static.com/fccf6e4a-5e63-40af-919b-d283ce640fd0/stn-ScRfAsXHEjJmVL7JjfkV7iSvfFe2qxik7ZoPS4S0.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220528%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220528T030949Z&X-Amz-Expires=3600&X-Amz-Signature=1f441325ffb26c27d7b618b2bc4c9dbb3b4516b3ffc63a5b59407bec346cf0eb&X-Amz-SignedHeaders=host&x-id=GetObject
#
