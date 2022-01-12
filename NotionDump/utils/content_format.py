# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

# 获取mention的格式
def get_mention_format(mention_content):
    return "@(" + mention_content + ")"


# 获取page的格式 运行过程中只填充id，后续调整页面供定位使用
def get_page_format_md(page_id):
    return "[" + page_id + "]()"


# 获取page的格式 纯文本只填充名字即可
def get_page_format_plain(page_name):
    return page_name


# 封装URL的格式
def get_url_format(url_plain, name="link"):
    return "[" + name + "](" + url_plain + ")"


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


# 行内公式格式
def get_equation_inline(equation):
    return "$ " + equation + " $"


# 块级公式格式
def get_equation_block(equation):
    return "<center>$$ " + equation + " $$</center>"
