# author: delta1037
# Date: 2022/01/09
# mail:geniusrabbit@qq.com

import copy
import json
from json import JSONDecodeError

import NotionDump
from NotionDump.utils import internal_var


# 更新子页面的状态
def update_child_page_stats(child_key, dumped=False, main_page=False, local_path=None, page_type=None):
    if child_key not in internal_var.PAGE_DIC:
        # 如果现有的列表里没有这一条,则新加一条
        debug_log("CREATE child page " + child_key + "from temp", level=NotionDump.DUMP_MODE_DEFAULT)
        internal_var.PAGE_DIC[child_key] = copy.deepcopy(internal_var.CHILD_PAGE_TEMP)
    internal_var.PAGE_DIC[child_key]["dumped"] = dumped
    internal_var.PAGE_DIC[child_key]["main_page"] = main_page
    if local_path is not None:
        internal_var.PAGE_DIC[child_key]["local_path"] = local_path
    if page_type is not None:
        if page_type == "block" or page_type == "page":
            internal_var.PAGE_DIC[child_key]["type"] = "page"
        elif page_type == "database":
            internal_var.PAGE_DIC[child_key]["type"] = "database"
        else:
            debug_log("update_child_page_stats page type is unknown:" + str(page_type), level=NotionDump.DUMP_MODE_DEFAULT)


# 关于软连接一共有如下情况
# 同一个页面：add_new_child_page
# 在同一个页面中，软连接先于实际链接出现
#   软连接先占位，把实际链接加进去
# 在同一个页面中，软连接在实际链接后出现
# 不同的页面：update_child_pages
# 在不同页面中，软连接先于实际链接出现
#   实际链接替换，重新解析
# 在不同页面中，软连接在实际链接后出现
#   忽略软连接
# 只出现软连接而没有出现实际链接，pass
def update_child_pages(child_pages, parent_id):
    # 按理说这里一定会有父id，如果没有就是出大事了
    if parent_id not in internal_var.PAGE_DIC:
        debug_log("parent id" + parent_id + " not exist!!!", level=NotionDump.DUMP_MODE_DEFAULT)
        return

    for child_page_id in child_pages:
        # 如果发现表里已经有了该页面，看是不是软链接创建的
        if child_page_id in internal_var.PAGE_DIC:
            # 如果页表里是软连接创建的，并且外面的不是软连接创建的
            # 如果里面是硬链接，外面是软连接则会忽略
            if internal_var.PAGE_DIC[child_page_id]["inter_soft_page"] \
                    and not child_pages[child_page_id]["inter_soft_page"]:
                # 将外面的合入到页面表，替换之后会重新解析，不用担心已经解析过的内容
                # 这里相当于填充了一个未开始解析的内容，而调用这个函数之后
                # __recursion_mix_parser会在循环遍历一次，将这个页面重新解析
                internal_var.PAGE_DIC[child_page_id] = child_pages[child_page_id]
                debug_log("REPLACE last created soft page, id=" + child_page_id, level=NotionDump.DUMP_MODE_DEFAULT)

        # 包括占位的类型，如果总页面表里不存在都放进去
        if child_page_id not in internal_var.PAGE_DIC:
            # 如果现有的列表里没有这一条,则新加一条
            debug_log("CREATE child page " + child_page_id + " from child_pages", level=NotionDump.DUMP_MODE_DEFAULT)
            internal_var.PAGE_DIC[child_page_id] = copy.deepcopy(child_pages[child_page_id])

        # 如果该页面是占位的，则不加到父页面表里
        if not child_pages[child_page_id]["inter_soft_page"]:
            debug_log("parent id" + parent_id + " add child " + child_page_id,
                      level=NotionDump.DUMP_MODE_DEFAULT)
            internal_var.PAGE_DIC[parent_id]["child_pages"].append(child_page_id)
        else:
            debug_log("SOFT_PAGE " + child_page_id + " dont need to add to parent_id " + parent_id,
                      level=NotionDump.DUMP_MODE_DEFAULT)


# 添加一个新的子页
# 链接的key格式是 id_链接名
# 子页面的key格式是id
def add_new_child_page(child_pages, key_id, link_id=None, link_src=None, page_name=None, page_type=None, inter_soft_page=False):
    # 判断id是否存在，存在就不添加了，防止覆盖
    debug_log("add new child key:" + key_id)
    # id 存在并且不是软连接创建的，就不添加了（硬链接先于软连接）
    if key_id in child_pages and not child_pages[key_id]["inter_soft_page"]:
        debug_log("WARN key_id:" + key_id + " exist, skip", level=NotionDump.DUMP_MODE_DEFAULT)
        return
    # 如果不存在或者上一个是软连接创建的，就重新赋值
    child_pages[key_id] = copy.deepcopy(internal_var.CHILD_PAGE_TEMP)
    child_pages[key_id]["inter_soft_page"] = inter_soft_page
    if link_id is not None:
        # 如果是软链接，递归看一下对应的子页面在不在,如果不在就先占个坑(忽略file和image类型)
        # inter_soft_page 表明该项是软连接创建的
        debug_log("SOFT_PAGE key_id " + key_id + " link_id " + link_id + ", create a null page with link_id",
                  level=NotionDump.DUMP_MODE_DEFAULT)
        add_new_child_page(child_pages, key_id=link_id, link_src=link_src, page_type=page_type, inter_soft_page=True)
    if page_name is not None:
        child_pages[key_id]["page_name"] = page_name
    if link_id is not None:
        child_pages[key_id]["link_id"] = link_id
    if link_src is not None:
        child_pages[key_id]["link_src"] = link_src
    if page_type is not None:
        child_pages[key_id]["type"] = page_type


# 用此函数的前提是page表中已经存在
def update_page_recursion(page_id, recursion=False):
    if page_id not in internal_var.PAGE_DIC:
        debug_log("page id not exist!!!", level=NotionDump.DUMP_MODE_DEFAULT)
        return
    internal_var.PAGE_DIC[page_id]["inter_recursion"] = recursion


def is_page_recursion(page_id):
    if page_id not in internal_var.PAGE_DIC:
        debug_log("page id not exist!!!", level=NotionDump.DUMP_MODE_DEFAULT)
        return False
    return not internal_var.PAGE_DIC[page_id]["inter_recursion"]


# page 返回True，DB返回False
def is_page(page_id):
    if page_id not in internal_var.PAGE_DIC:
        debug_log("page id not exist!!!", level=NotionDump.DUMP_MODE_DEFAULT)
        return False
    return internal_var.PAGE_DIC[page_id]["type"] == "page"


# database 返回True
def is_db(db_id):
    if db_id not in internal_var.PAGE_DIC:
        debug_log("db_id not exist!!!", level=NotionDump.DUMP_MODE_DEFAULT)
        return False
    return internal_var.PAGE_DIC[db_id]["type"] == "database"


# database 返回True
def is_download(download_id):
    if download_id not in internal_var.PAGE_DIC:
        debug_log("download_id not exist!!!", level=NotionDump.DUMP_MODE_DEFAULT)
        return False
    # 可下载类型
    return internal_var.PAGE_DIC[download_id]["type"] == "image" or internal_var.PAGE_DIC[download_id]["type"] == "file"


# 判断是否是链接页面
def is_link_page(page_id, page_handle):
    return (page_id.find("_") != -1) and page_handle["link_id"] != ""


# 将文本保存为json文件
def save_json_to_file(handle, json_name):
    try:
        json_handle = json.dumps(handle, ensure_ascii=False, indent=4)
    except JSONDecodeError:
        debug_log("json decode error", level=NotionDump.DUMP_MODE_DEFAULT)
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


def debug_log(debug_str, level=NotionDump.DUMP_MODE_DEBUG):
    if NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEBUG:
        # debug 模式啥都打印出来
        print("[NotionDump] ", end='')
        print(debug_str)

        # debug内容写入到文件
        log_fd = open("notion-export-kernel-debug.log", "a+", encoding='utf-8')
        log_fd.write(str(debug_str) + "\n")
        log_fd.flush()
        log_fd.close()

    elif NotionDump.DUMP_MODE == NotionDump.DUMP_MODE_DEFAULT and level == NotionDump.DUMP_MODE_DEFAULT:
        # 默认模式 对 level进行过滤
        print("[NotionDump] ", end='')
        print(debug_str)
    # 静默模式什么都不输出
