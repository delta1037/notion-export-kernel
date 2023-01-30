# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

__author__ = "delta1037 <geniusrabbit@qq.com>"
__version__ = "0.2.1"

# 临时存放文件夹
TMP_DIR = "./.tmp/"

# Markdown的分割条语法
MD_DIVIDER = "------"
MD_BOOL_TRUE = "✓"
MD_BOOL_FALSE = "✕"
# ,、<br> 逗号或者换行
MD_ROLLUP_SEP = ","
MD_HIGHLIGHT = "=="
ID_LEN = len("921e6b4ea44046c6935bcb2c69453196")

# 日志输出模式
DUMP_MODE_DEBUG = 0
DUMP_MODE_DEFAULT = 1
DUMP_MODE_SILENT = 2
DUMP_MODE = DUMP_MODE_DEFAULT

# 导出的类型
DUMP_TYPE_BLOCK = 1
DUMP_TYPE_PAGE = 2
DUMP_TYPE_DB_TABLE = 4

# 解析的类型：分为Markdown和纯文本
PARSER_TYPE_MD = 0
PARSER_TYPE_PLAIN = 2

# 是否使用缓存
BUFFER_FILE = TMP_DIR + "notion_download_buffer.json"
USE_BUFFER = True

# 一些配置开关
# 对没有在notion保存的文件(pdf\image)尝试下载，否则直接放置链接
FILE_WITH_LINK = True
FORMAT_DATE = "%Y/%m/%d"
FORMAT_DATETIME = "%Y/%m/%d-%H:%M:%S"
# 是否导出page的properties
S_PAGE_PROPERTIES = True
# 主题的格式，default，light，dark，markdown，self_define
S_THEME_TYPE = "default"
# f开头的是字体颜色，b开头的是背景颜色，d开头的是数据库标签
S_THEME_LIGHT = {
    "f_gray": "#787774",
    "f_brown": "#9F6B53",
    "f_orange": "#D9730D",
    "f_yellow": "#CB912F",
    "f_green": "#448361",
    "f_blue": "#337EA9",
    "f_purple": "#9065B0",
    "f_pink": "#C14C8A",
    "f_red": "#D44C47",
    "b_gray": "#F1F1EF",
    "b_brown": "#F4EEEE",
    "b_orange": "#FBECDD",
    "b_yellow": "#FBF3DB",
    "b_green": "#EDF3EC",
    "b_blue": "#E7F3F8",
    "b_purple": "#F4F0F7CC",
    "b_pink": "#F9EEF3CC",
    "b_red": "#FDEBEC",
    "d_light_gray": "#E3E2E080",
    "d_gray": "#E3E2E0",
    "d_brown": "#EEE0DA",
    "d_orange": "#FADEC9",
    "d_yellow": "#FDECC8",
    "d_green": "#DBEDDB",
    "d_blue": "#D3E5EF",
    "d_purple": "#E8DEEE",
    "d_pink": "#F5E0E9",
    "d_red": "#FFE2DD",
}

S_THEME_DARK = {
    "f_gray": "#9B9B9B",
    "f_brown": "#BA856F",
    "f_orange": "#C77D48",
    "f_yellow": "#CA9849",
    "f_green": "#529E72",
    "f_blue": "#5E87C9",
    "f_purple": "#9D68D3",
    "f_pink": "#D15796",
    "f_red": "#DF5453",
    "b_gray": "#2F2F2F",
    "b_brown": "#4A3228",
    "b_orange": "#5C3B23",
    "b_yellow": "#564328",
    "b_green": "#243D30",
    "b_blue": "#143A4E",
    "b_purple": "#3C2D49",
    "b_pink": "#4E2C3C",
    "b_red": "#522E2A",
    "d_light_gray": "#373737",
    "d_gray": "#5A5A5A",
    "d_brown": "#603B2C",
    "d_orange": "#854C1D",
    "d_yellow": "#89632A",
    "d_green": "#2B593F",
    "d_blue": "#28456C",
    "d_purple": "#492F64",
    "d_pink": "#69314C",
    "d_red": "#6E3630",
}

S_THEME_SELF_DEFINE = {
    "f_gray": "#787774",
    "f_brown": "#9F6B53",
    "f_orange": "#D9730D",
    "f_yellow": "#CB912F",
    "f_green": "#448361",
    "f_blue": "#337EA9",
    "f_purple": "#9065B0",
    "f_pink": "#C14C8A",
    "f_red": "#D44C47",
    "b_gray": "#F1F1EF",
    "b_brown": "#F4EEEE",
    "b_orange": "#FBECDD",
    "b_yellow": "#FBF3DB",
    "b_green": "#EDF3EC",
    "b_blue": "#E7F3F8",
    "b_purple": "#F4F0F7CC",
    "b_pink": "#F9EEF3CC",
    "b_red": "#FDEBEC",
    "d_light_gray": "#E3E2E080",
    "d_gray": "#E3E2E0",
    "d_brown": "#EEE0DA",
    "d_orange": "#FADEC9",
    "d_yellow": "#FDECC8",
    "d_green": "#DBEDDB",
    "d_blue": "#D3E5EF",
    "d_purple": "#E8DEEE",
    "d_pink": "#F5E0E9",
    "d_red": "#FFE2DD",
}
