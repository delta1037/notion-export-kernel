# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

import os
import urllib.request

import NotionDump
from NotionDump.utils import common_op


class DownloadParser:
    def __init__(self, download_id):
        self.download_id = download_id

        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    def download_to_file(self, new_id, child_page_item):
        # 解析文件后缀名
        file_url = child_page_item["link_id"]
        common_op.debug_log("download url is " + file_url, level=NotionDump.DUMP_MODE_DEBUG)
        if file_url == "":
            return ""
        # 文件名在最后一个/和?之间
        filename = file_url[file_url.rfind('/')+1:file_url.find('?')]
        file_suffix = filename[filename.find('.'):]
        # 使用后缀和id生成可识别的文件
        download_name = self.tmp_dir + new_id + file_suffix
        common_op.debug_log("download name " + download_name, level=NotionDump.DUMP_MODE_DEBUG)
        # 下载文件
        urllib.request.urlretrieve(file_url, download_name)
        return download_name
