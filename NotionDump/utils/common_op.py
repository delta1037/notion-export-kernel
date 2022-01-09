# author: delta1037
# Date: 2022/01/09
# mail:geniusrabbit@qq.com
import copy
import NotionDump


# 更新子页面的状态
def update_child_page_stats(child_pages, child_key, dumped=False):
    if child_key not in child_pages:
        # 如果现有的列表里没有这一条,则新加一条
        child_pages[child_key] = copy.deepcopy(NotionDump.CHILD_PAGE_TEMP)
    child_pages[child_key]["dumped"] = dumped
