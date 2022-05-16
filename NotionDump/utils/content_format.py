# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import datetime

import dateutil.parser


# 获取mention的格式
import NotionDump


def get_mention_format(mention_content):
    return "@(" + mention_content + ")"


# 获取page的格式 运行过程中只填充id，后续调整页面供定位使用
def get_page_format_md(page_id, page_name, export_child):
    if export_child:
        return "[" + page_id + "]()"
    else:
        return "[" + page_name + "](" + page_id + ")"


# 数据库title格式
def get_database_title_format(title_id, title_ret, export_child):
    if export_child:
        return "[" + title_id + "]()"
    else:
        # 不导出子页面直接把标题填上去
        return title_ret


# 获取page的格式 纯文本只填充名字即可
def get_page_format_plain(page_name):
    return page_name


# 封装URL的格式
def get_url_format(url_plain, name="link"):
    return "[" + name + "](" + url_plain + ")"


def format_date_or_time(date_time):
    # print(date_time)
    t_datetime = dateutil.parser.parse(date_time)
    # print(date_time, t_datetime)
    if date_time.find('T') != -1:
        # datetime
        return t_datetime.strftime(NotionDump.FORMAT_DATETIME)
    else:
        # date
        return t_datetime.strftime(NotionDump.FORMAT_DATE)


# 封装date的格式
def get_date_format(start, end):
    ret_str = ""
    if start is not None:
        ret_str = format_date_or_time(start)
    if end is not None:
        ret_str += " ~ " + format_date_or_time(end)  # 日期之间用“~”分割
    return ret_str


# 封装文件链接格式
def get_file_format_md(filename, file_url, file_id="", export_child=False):
    if export_child:
        if file_id == "":
            return "[" + filename + "](" + file_url + ")"
        else:
            # 等待重定位
            return "[" + file_id + "]()"
    else:
        # 不导出子页面直接把标题填上去
        return "[" + filename + "](" + file_url + ")"


# 封装文件链接格式
def get_file_format_plain(filename, file_url):
    return filename + "(" + file_url + ")"


# 行内公式格式
def get_equation_inline(equation):
    return "$ " + equation + " $"


# 块级公式格式
def get_equation_block(equation):
    return "$$ " + equation + " $$"


def color_transformer(input_color, background=False):
    if input_color == "gray":
        if background:
            return "#F1F1EF"
        else:
            return "#787774"
    if input_color == "brown":
        if background:
            return "#F4EEEE"
        else:
            return "#9F6B53"
    if input_color == "orange":
        if background:
            return "#FBECDD"
        else:
            return "#D9730D"
    if input_color == "yellow":
        if background:
            return "#FBF3DB"
        else:
            return "#CB912F"
    if input_color == "green":
        if background:
            return "#EDF3EC"
        else:
            return "#448361"
    if input_color == "blue":
        if background:
            return "#E7F3F8"
        else:
            return "#337EA9"
    if input_color == "purple":
        if background:
            return "#F4F0F7CC"
        else:
            return "#9065B0"
    if input_color == "pink":
        if background:
            return "#F9EEF3CC"
        else:
            return "#C14C8A"
    if input_color == "red":
        if background:
            return "#FDEBEC"
        else:
            return "#D44C47"
    return input_color


def color_transformer_db(input_color):
    if input_color == "default":
        return "#E3E2E080"
    if input_color == "gray":
        return "#E3E2E0"
    if input_color == "brown":
        return "#EEE0DA"
    if input_color == "orange":
        return "#FADEC9"
    if input_color == "yellow":
        return "#FDECC8"
    if input_color == "green":
        return "#DBEDDB"
    if input_color == "blue":
        return "#D3E5EF"
    if input_color == "purple":
        return "#E8DEEE"
    if input_color == "pink":
        return "#F5E0E9"
    if input_color == "red":
        return "#FFE2DD"
    return input_color
