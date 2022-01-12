# author: delta1037
# Date: 2022/01/09
# mail:geniusrabbit@qq.com
import copy
import json
import logging
from json import JSONDecodeError

import NotionDump
from NotionDump.utils import internal_var


# 更新子页面的状态
def update_child_page_stats(child_key, dumped=False, main_page=False, local_path=None):
    if child_key not in internal_var.PAGE_DIC:
        # 如果现有的列表里没有这一条,则新加一条
        internal_var.PAGE_DIC[child_key] = copy.deepcopy(internal_var.CHILD_PAGE_TEMP)
    internal_var.PAGE_DIC[child_key]["dumped"] = dumped
    internal_var.PAGE_DIC[child_key]["main_page"] = main_page
    if local_path is not None:
        internal_var.PAGE_DIC[child_key]["local_path"] = local_path


def update_child_pages(child_pages, parent_id):
    # 按理说这里一定会有父id，如果没有就是出大事了
    if parent_id not in internal_var.PAGE_DIC:
        logging.log(logging.ERROR, "parent id not exist!!!")
        return

    for child_page_id in child_pages:
        if child_page_id not in internal_var.PAGE_DIC:
            # 如果现有的列表里没有这一条,则新加一条
            internal_var.PAGE_DIC[child_page_id] = copy.deepcopy(child_pages[child_page_id])
        # 将子页面添加到父页面的列表里
        # print("before add")
        # print(NotionDump.utils.internal_var.PAGE_DIC)
        internal_var.PAGE_DIC[parent_id]["child_pages"].append(child_page_id)
        # print("after add")
        # print(NotionDump.utils.internal_var.PAGE_DIC)


# 添加一个新的子页
# 链接的key格式是 id_链接名
# 子页面的key格式是id
def add_new_child_page(child_pages, key_id, page_id=None, link_id=None, page_name=None, page_type=None):
    # 判断id是否存在，存在就不添加了，防止覆盖
    if key_id in child_pages:
        logging.log(logging.WARN, "warn key_id:" + key_id + " exist, skip")
        # 看一下页面名字有没有,如果名字是空的就是之前占坑的,把名字填进去
        if child_pages[key_id]["page_name"] == "" and page_name is not None:
            child_pages[key_id]["page_name"] = page_name
        return
    child_pages[key_id] = copy.deepcopy(internal_var.CHILD_PAGE_TEMP)
    if page_id is None:
        # 说明此时是一个子页面
        page_id = key_id
    else:
        # 如果是链接，递归看一下对应的子页面在不在,如果在就先占个坑
        debug_log("### link type key_id: " + key_id + " page_id:" + page_id)
        add_new_child_page(child_pages, key_id=page_id, page_type=page_type)
    if page_name is not None:
        child_pages[key_id]["page_name"] = page_name
    if link_id is not None:
        child_pages[key_id]["link_id"] = link_id
    if page_type is not None:
        child_pages[key_id]["type"] = page_type


# 用此函数的前提是page表中已经存在
def update_page_recursion(page_id, recursion=False):
    if page_id not in internal_var.PAGE_DIC:
        logging.log(logging.ERROR, "page id not exist!!!")
        return
    internal_var.PAGE_DIC[page_id]["page_recursion"] = recursion


def is_page_recursion(page_id):
    if page_id not in internal_var.PAGE_DIC:
        logging.log(logging.ERROR, "page id not exist!!!")
        return False
    return not internal_var.PAGE_DIC[page_id]["page_recursion"]


# page 返回True，DB返回False
def is_page(page_id):
    if page_id not in internal_var.PAGE_DIC:
        logging.log(logging.ERROR, "page id not exist!!!")
        return True
    return internal_var.PAGE_DIC[page_id]["type"] == "page"


# 判断是否是链接页面
def is_link_page(page_id, page_handle):
    return (page_id.find("_") != -1) and page_handle["link_id"] != ""


# 将文本保存为json文件
def save_json_to_file(handle, json_name):
    try:
        json_handle = json.dumps(handle, ensure_ascii=False, indent=4)
    except JSONDecodeError:
        print("json decode error")
        return

    file = open(json_name, "w+", encoding="utf-8")
    file.write(json_handle)
    file.flush()
    file.close()


# 判断是否添加额外的换行
def parser_newline(last_type, now_type):
    if last_type == "to_do" and now_type == "to_do":
        return False
    if last_type == "numbered_list_item" and now_type == "numbered_list_item":
        return False
    if last_type == "bulleted_list_item" and now_type == "bulleted_list_item":
        return False
    if last_type == "toggle" and now_type == "toggle":
        return False
    # 处理表格类型
    if last_type == "table" and now_type == "table_row":
        return False
    if last_type == "table_row" and now_type == "table_row":
        return False
    return True


def debug_log(debug_str):
    if NotionDump.DUMP_DEBUG:
        print(debug_str)
