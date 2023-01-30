from time import strftime, localtime

import NotionDump
from NotionDump.utils import common_op


class Buffer:
    def __init__(self):
        self.base_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.buffer_map = common_op.load_json_from_file(NotionDump.BUFFER_FILE)
        if self.buffer_map is None:
            self.buffer_map = {}

    def save_buffer(self):
        common_op.debug_log("save buffer file")
        common_op.save_json_to_file(self.buffer_map, NotionDump.BUFFER_FILE)

    def add_buffer(self, page_id, page_time, id_type="page"):
        if page_id not in self.buffer_map:
            common_op.debug_log("[BUFFER] add_buffer, new, id=" + page_id + ", type=" + id_type)
            self.buffer_map[page_id] = {
                "type": id_type,
                # 页面上次编辑时间
                "last_edited_time": page_time,
                # 页面上次下载时间
                "update_time": None,
                # 页面脏标志
                "dirty": True
            }
        else:
            if page_time != self.buffer_map[page_id]["last_edited_time"]:
                # 页面编辑过，需要重新下载
                common_op.debug_log("[BUFFER] add_buffer, update, id=" + page_id + ", type=" + id_type)
                self.buffer_map[page_id]["dirty"] = True
                self.buffer_map[page_id]["last_edited_time"] = page_time

    def update_buffer(self, page_id):
        # 文件已重新下载，设置更新时间
        if page_id in self.buffer_map:
            common_op.debug_log("[BUFFER] update_buffer, id=" + page_id)
            self.buffer_map[page_id]["update_time"] = strftime("%Y-%m-%d %H:%M:%S", localtime())
            self.buffer_map[page_id]["dirty"] = False

    def select_buffer(self, page_id, is_child=False):
        # 查看缓存中是否命中，命中返回True（说明缓存有效），没命中返回False（说明缓存文件无效，需要重新下载）
        if page_id not in self.buffer_map:
            common_op.debug_log("[BUFFER] select_buffer, id=" + page_id + ", not exist")
            return False
        else:
            if is_child:
                if self.buffer_map[page_id]["update_time"] >= self.base_time:
                    # 子块所在的页面刚更新过，子块也要随之更新
                    common_op.debug_log("[BUFFER] select_buffer, child update, id=" + page_id)
                    return True
                else:
                    common_op.debug_log("[BUFFER] select_buffer, child old, id=" + page_id)
                    return self.buffer_map[page_id]["dirty"]
            else:
                common_op.debug_log("[BUFFER] select_buffer, main, id=" + page_id)
                return self.buffer_map[page_id]["dirty"]
