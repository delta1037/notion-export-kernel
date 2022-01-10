# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

# 解析的类型：分为Markdown和纯文本
PARSER_TYPE_MD = 0
PARSER_TYPE_PLAIN = 2

# 导出页面结构
PAGE_DIC = {}

# 导出页面列表的格式
CHILD_PAGE_TEMP = {
    "dumped": False,
    "main_page": False,
    "page_recursion": False,
    "type": "page",
    "local_path": "",
    "page_name": "",
    "child_pages": []
}
