# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

# 获取本地链接的格式
def get_page_local_path(page_id):
    return "./page_" + page_id.replace('-', '') + ".md"


# 获取mention的格式
def get_mention_format(mention_content):
    return "@(" + mention_content + ")"


# 获取page的格式
def get_page_format_md(page_name, page_url):
    return "[" + page_name + "](" + page_url + ")"


# 获取page的格式
def get_page_format_plain(page_name, page_url):
    return page_name + "(" + page_url + ")"


# 封装URL的格式
def get_url_format(url_plain):
    return "[link](" + url_plain + ")"


# 封装date的格式
def get_date_format(start, end):
    ret_str = ""
    if start is not None:
        ret_str = start
    if end is not None:
        ret_str += " ~ " + end  # 日期之间用“~”分割
    return ret_str


# 封装文件链接格式
def get_file_format_md(filename, file_url):
    return "[" + filename + "](" + file_url + ")"


# 封装文件链接格式
def get_file_format_plain(filename, file_url):
    return filename + "(" + file_url + ")"
