# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

# ms
FRIENDLY_USE_API = 350

# 导出页面结构
PAGE_DIC = {}

# 导出页面列表的格式
CHILD_PAGE_TEMP = {
    "dumped": False,
    "main_page": False,
    "type": "page",
    "local_path": "",
    "page_name": "",
    "link_id": "",
    "child_pages": [],
    "inter_recursion": False,
    "inter_soft_page": False
}
# inter_soft_link 表示该页是由链接创建的
