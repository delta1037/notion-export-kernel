# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import copy

import NotionDump
from NotionDump.utils import content_format, common_op
from NotionDump.utils import internal_var
from urllib.parse import unquote
from NotionDump.utils.content_format import color_transformer, color_transformer_db


class BaseParser:
    def __init__(self, base_id, export_child=False):
        self.base_id = base_id.replace('-', '')
        self.export_child = export_child

        # 设置变量存放子page 字典
        self.child_pages = {}

    def set_new_id(self, parent_id):
        self.base_id = parent_id

    # 获取子页面字典，只返回一次，离台概不负责
    def get_child_pages_dic(self):
        child_pages = copy.deepcopy(self.child_pages)
        self.child_pages.clear()  # 清空已有的内容
        return child_pages

    # 文本的格式生成
    @staticmethod
    def __annotations_parser(block_handle, str_plain):
        if str_plain is None or str_plain == "":
            return ""
        last_char = str_plain[-1:]
        if last_char == "\n" or last_char == "\t":
            str_ret = str_plain[0:-1]
        else:
            str_ret = str_plain
        if block_handle["code"]:
            str_ret = "`" + str_ret + "`"
        if block_handle["underline"]:
            str_ret = "<u>" + str_ret + "</u>"
        if block_handle["bold"]:
            str_ret = "**" + str_ret + "**"
        if block_handle["italic"]:
            str_ret = "*" + str_ret + "*"
        if block_handle["color"] != "default":
            # 添加颜色，区分背景色和前景色
            if block_handle["color"].find("_background") != -1:
                bg_color = block_handle["color"][0:block_handle["color"].rfind('_')]
                str_ret = "<span style=\"background-color:" + color_transformer(bg_color, background=True) + "\">" + str_ret + "</span>"
            else:
                str_ret = "<font color=\"" + color_transformer(block_handle["color"], background=False) + "\">" + str_ret + "</font>"
        if block_handle["strikethrough"]:
            str_ret = "~~" + str_ret + "~~"
        if last_char == "\n" or last_char == "\t":
            str_ret += last_char
        return str_ret

    def __text_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "text":
            common_op.debug_log(
                "text type error! id=" + self.base_id + " not type " + block_handle["type"],
                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""

        text_str = ""
        if "plain_text" in block_handle:
            text_str = block_handle["plain_text"]
        if text_str is None:
            text_str = ""
        # 如果有链接
        text_url = block_handle["href"]
        if text_url is not None and parser_type == NotionDump.PARSER_TYPE_MD:
            # 文字有链接内容，分为网络链接和本地链接
            if text_url.startswith("http"):
                # 网络链接，直接一步到位
                text_str = content_format.get_url_format(text_url, text_str)
            else:
                # Page或者数据库类型，等待重定位
                if text_url.find("=") != -1:
                    page_id = text_url[text_url.rfind("/") + 1:text_url.rfind("?")]
                    common_op.debug_log("### page id " + page_id + " is database")
                    common_op.add_new_child_page(
                        self.child_pages,
                        key_id=page_id + "_" + text_str,
                        link_id=page_id,
                        link_src=text_url,
                        page_type="database",
                        page_name=text_str
                    )
                else:
                    page_id = text_url[text_url.rfind("/") + 1:]
                    common_op.debug_log("### page id " + page_id + " is page")
                    common_op.add_new_child_page(
                        self.child_pages,
                        key_id=page_id + "_" + text_str,
                        link_id=page_id,
                        link_src=text_url,
                        page_type="page",
                        page_name=text_str
                    )

                # 将页面保存，等待进一步递归操作
                # 保存子页面信息
                common_op.debug_log("child_page_parser add page id = " + page_id + "_" + text_str, level=NotionDump.DUMP_MODE_DEFAULT)
                text_str = content_format.get_page_format_md(page_id + "_" + text_str, text_str,
                                                             export_child=self.export_child)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            # 解析annotations部分，为text_str添加格式
            return self.__annotations_parser(block_handle["annotations"], text_str)
        else:
            return text_str

    def __text_block_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN, is_db=False):
        paragraph_ret = ""
        if block_handle["type"] == "text":
            paragraph_ret = self.__text_parser(block_handle, parser_type)
        elif block_handle["type"] == "equation":
            paragraph_ret = self.__equation_inline_parser(block_handle)
        elif block_handle["type"] == "mention":
            paragraph_ret = self.__mention_parser(block_handle, parser_type, is_db=is_db)
        else:
            common_op.debug_log(
                "text type " + block_handle["type"] + " error! parent_id= " + self.base_id,
                level=NotionDump.DUMP_MODE_DEFAULT)
        return paragraph_ret

    def __text_list_parser(self, text_list, parser_type=NotionDump.PARSER_TYPE_PLAIN, is_db=False):
        plain_text = ""
        if text_list is not None:
            for text_block in text_list:
                plain_text += self.__text_block_parser(text_block, parser_type, is_db=is_db)
        if is_db:
            # 数据库内容特殊字符校对
            return plain_text.replace("|", "\\|")
        else:
            return plain_text

    # TODO : people只获取了名字和ID，后续可以做深度解析用户相关内容
    def __people_parser(self, block_handle):
        if block_handle["object"] != "user":
            common_op.debug_log("people type error! id=" + self.base_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        # 优先获取名字
        if "name" in block_handle.keys():
            return block_handle["name"]
        # 如果无法获取名字则返回id
        return block_handle["id"].replace('-', '')

    def __user_parser(self, block_handle):
        if block_handle["type"] != "user":
            common_op.debug_log("user type error! id=" + self.base_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        user_body = block_handle["user"]
        return self.__people_parser(user_body)

    def __db_file_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "file":
            common_op.debug_log("file type error! id=" + self.base_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        filename = block_handle["name"]
        file_url = block_handle["file"]["url"]

        # 解析文件的ID
        url_prefix = file_url[0:file_url.rfind("/")]
        file_id = url_prefix[url_prefix.rfind("/") + 1:].replace('-', '')
        common_op.debug_log("file id is : " + file_id)

        if filename == "":
            # 如果文件没有名字使用id作为默认名字
            filename = file_id
        common_op.add_new_child_page(
            self.child_pages,
            key_id=file_id,
            link_src=file_url,
            page_type="file",
            page_name=filename
        )
        common_op.debug_log(
            "file_parser add page id = " + file_id + " name : " + filename, level=NotionDump.DUMP_MODE_DEFAULT)
        common_op.debug_log(internal_var.PAGE_DIC)
        common_op.debug_log("#############")
        common_op.debug_log(self.child_pages)

        # 格式处理简单格式（也可以转换成markdown格式[]()）
        if parser_type == NotionDump.PARSER_TYPE_MD:
            # file转换成文件链接的形式
            return content_format.get_file_format_md(filename, file_url, file_id, self.export_child)
        else:
            return content_format.get_file_format_plain(filename, file_url)

    # "$ equation_inline $"
    def __equation_inline_parser(self, block_handle):
        if block_handle["type"] != "equation":
            common_op.debug_log("equation inline type error! id=" + self.base_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        # 公式删除富文本格式
        # return content_format.get_equation_inline(
        #     self.__annotations_parser(block_handle["annotations"], block_handle["plain_text"])
        # )
        return content_format.get_equation_inline(block_handle["plain_text"])

    # "$$ equation_block $$"
    def __equation_block_parser(self, block_handle):
        if block_handle["expression"] is None:
            common_op.debug_log("equation block no expression! id=" + self.base_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        return content_format.get_equation_block(block_handle["expression"])

    # Attention!!! 关于链接到其它的Page可能需要递归处理
    def __page_parser(self, block_handle):
        if block_handle["type"] != "page":
            common_op.debug_log("page type error! parent_id= " + self.base_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""

        page_body = block_handle["page"]
        return page_body["id"].replace('-', '')

    # 提及到其它页面，日期，用户
    def __mention_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN, is_db=False):
        if block_handle["type"] != "mention":
            common_op.debug_log("mention type error! parent_id= " + self.base_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""

        mention_body = block_handle["mention"]
        mention_plain = ""
        if mention_body["type"] == "date":
            mention_plain = self.date_parser(mention_body)
        elif mention_body["type"] == "user":
            mention_plain = self.__user_parser(mention_body)
        elif mention_body["type"] == "link_preview" and "url" in mention_body["link_preview"].keys():
            mention_plain = mention_body["link_preview"]["url"]
        elif mention_body["type"] == "database":
            database_id = mention_body["database"]["id"].replace('-', '')
            key_id = database_id + "_mention"
            common_op.debug_log("__mention_parser add database id = " + database_id)
            # 获取页面的名字
            database_name = block_handle["plain_text"]
            database_link = block_handle["href"]

            common_op.add_new_child_page(
                self.child_pages,
                key_id=key_id,
                link_id=database_id,
                link_src=database_link,
                page_type="database",
                page_name=database_name
            )
            common_op.debug_log(
                "file_parser add page id = " + key_id + " name : " + database_name, level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(internal_var.PAGE_DIC)
            common_op.debug_log("#############")
            common_op.debug_log(self.child_pages)

            if parser_type == NotionDump.PARSER_TYPE_MD:
                mention_plain = content_format.get_page_format_md(key_id, database_name, export_child=self.export_child)
            else:
                mention_plain = database_name
        elif mention_body["type"] == "page":
            page_id = self.__page_parser(mention_body)
            key_id = page_id + "_mention"
            common_op.debug_log("__mention_parser add page id = " + page_id)
            # 获取页面的名字
            page_name = block_handle["plain_text"]
            page_link = block_handle["href"]

            # 提及页面按照链接页面处理
            common_op.add_new_child_page(
                self.child_pages,
                key_id=key_id,
                link_id=page_id,
                link_src=page_link,
                page_type="page",
                page_name=page_name
            )
            common_op.debug_log(
                "file_parser add page id = " + key_id + " name : " + page_name, level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(internal_var.PAGE_DIC)
            common_op.debug_log("#############")
            common_op.debug_log(self.child_pages)

            if parser_type == NotionDump.PARSER_TYPE_MD:
                mention_plain = content_format.get_page_format_md(key_id, page_name, export_child=self.export_child)
            else:
                mention_plain = page_name
        else:
            common_op.debug_log("unknown mention type " + mention_body["type"], level=NotionDump.DUMP_MODE_DEFAULT)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            # 解析annotations部分，为mention_plain添加格式
            return self.__annotations_parser(block_handle["annotations"],
                                             content_format.get_mention_format(mention_plain))
        else:
            return content_format.get_mention_format(mention_plain)

    def __table_row_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "table_row":
            common_op.debug_log("table_row type error! parent_id= " + self.base_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        table_col_cells = block_handle["table_row"]["cells"]
        table_row = []
        for cell in table_col_cells:
            table_row.append(self.__text_list_parser(cell, parser_type))
        return table_row

    # 数据库 title
    def title_parser(self, block_handle, page_id, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "title":
            common_op.debug_log("title type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        db_page_title = self.__text_list_parser(block_handle["title"], parser_type, is_db=True)
        if db_page_title != "":
            # 如果存在子Page就加入到待解析队列
            common_op.debug_log("title ret = " + db_page_title)
            if parser_type != NotionDump.PARSER_TYPE_PLAIN:
                common_op.debug_log("title_parser add page id = " + page_id, level=NotionDump.DUMP_MODE_DEFAULT)
            else:
                common_op.debug_log("title_parser add page id = " + page_id)
            # 数据库里的都是子页面
            common_op.add_new_child_page(self.child_pages, key_id=page_id, page_name=db_page_title)

            # 如果有子页面就添加一个占位符，之后方便重定位
            db_page_title = content_format.get_database_title_format(page_id, db_page_title, self.export_child)
        return db_page_title

    # 数据库 rich_text
    def rich_text_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "rich_text":
            common_op.debug_log("rich_text type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        return self.__text_list_parser(block_handle["rich_text"], parser_type, is_db=True)

    # 数据库 multi_select
    def multi_select_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "multi_select":
            common_op.debug_log("multi_select type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        multi_select_list = block_handle["multi_select"]
        ret_str = ""
        if multi_select_list is None:
            return ret_str
        for multi_select in multi_select_list:
            if ret_str != "":
                ret_str += ","  # 多个选项之间用“,”分割
            if parser_type == NotionDump.PARSER_TYPE_MD and multi_select["color"] != "default":
                ret_str += "<span style=\"background-color:" \
                           + color_transformer_db(multi_select["color"]) \
                           + "\">" + multi_select["name"] + "</span>"
            else:
                ret_str += multi_select["name"]
        return ret_str

    # 数据库 select
    def select_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "select":
            common_op.debug_log("select type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        select = block_handle["select"]
        ret_str = ""
        if select is None:
            return ret_str
        if parser_type == NotionDump.PARSER_TYPE_MD and select["color"] != "default":
            ret_str = "<span style=\"background-color:" \
                + color_transformer_db(select["color"]) \
                + "\">" + select["name"] + "</span>"
        else:
            ret_str = select["name"]
        return ret_str

    # 数据库 url
    def url_parser(self, block_handle):
        if block_handle["type"] != "url":
            common_op.debug_log("url type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        url = block_handle["url"]
        if url is None:
            url = ""
        return content_format.get_url_format(url)

    # 数据库 email
    def email_parser(self, block_handle):
        if block_handle["type"] != "email":
            common_op.debug_log("email type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        email = block_handle["email"]
        ret_str = ""
        if email is not None:
            ret_str = email
        return ret_str

    # 数据库 checkbox
    def checkbox_parser(self, block_handle):
        if block_handle["type"] != "checkbox":
            common_op.debug_log("checkbox type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        checkbox = block_handle["checkbox"]
        if checkbox is True:
            ret_str = "true"
        else:
            ret_str = "false"
        return ret_str

    # 数据库 phone_number
    def phone_number_parser(self, block_handle):
        if block_handle["type"] != "phone_number":
            common_op.debug_log("phone_number type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        phone_number = block_handle["phone_number"]
        ret_str = ""
        if phone_number is not None:
            ret_str = phone_number
        return ret_str

    # 数据库 date
    def date_parser(self, block_handle):
        if block_handle["type"] != "date":
            common_op.debug_log("date type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        date = block_handle["date"]
        if date is None:
            return ""
        return content_format.get_date_format(date["start"], date["end"])

    # 数据库 people
    def people_parser(self, block_handle):
        if block_handle["type"] != "people":
            common_op.debug_log("people type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        people_list = block_handle["people"]
        ret_str = ""
        if people_list is None:
            return ret_str
        for people in people_list:
            if ret_str != "":
                ret_str += ","  # 多个用户之间用“,”分割
            ret_str += self.__people_parser(people)
        return ret_str

    # 数据库 number
    def number_parser(self, block_handle):
        if block_handle["type"] != "number":
            common_op.debug_log("number type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        number = block_handle["number"]
        ret_str = ""
        if number is None:
            return ret_str
        ret_str = number
        return ret_str

    # 数据库 files
    def files_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "files":
            common_op.debug_log("files type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        files_list = block_handle["files"]
        ret_str = ""
        if files_list is None:
            return ret_str
        for file in files_list:
            if ret_str != "":
                if parser_type == NotionDump.PARSER_TYPE_MD:
                    ret_str += "<br>"  # 多个文件之间用“<br>”分割
                else:
                    ret_str += ","  # 多个文件之间用“,”分割
            ret_str += self.__db_file_parser(file, parser_type)
        return ret_str

    # 数据库 rollup 数据
    def rollup_parser(self, block_handle):
        if block_handle["type"] != "rollup":
            common_op.debug_log("rollup type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        rollup_block = block_handle["rollup"]
        ret_str = ""
        if rollup_block[rollup_block["type"]] is None:
            return ret_str
        ret_str = rollup_block[rollup_block["type"]]
        return ret_str

    # 数据库 created_time
    def created_time_parser(self, block_handle):
        if block_handle["type"] != "created_time":
            common_op.debug_log("created_time type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        return block_handle["created_time"]

    # 数据库 last_edited_time
    def last_edited_time_parser(self, block_handle):
        if block_handle["type"] != "last_edited_time":
            common_op.debug_log(
                "last_edited_time type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        return block_handle["last_edited_time"]

    def created_by_parser(self, block_handle):
        if block_handle["type"] != "created_by":
            common_op.debug_log("created_by type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        return self.__people_parser(block_handle["created_by"])

    # 数据库 last_edited_by
    def last_edited_by_parser(self, block_handle):
        if block_handle["type"] != "last_edited_by":
            common_op.debug_log(
                "last_edited_by type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        return self.__people_parser(block_handle["last_edited_by"])

    # Page paragraph
    #   mention
    #       date
    #       user
    #       page
    #   text
    #   equation
    def paragraph_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        paragraph_ret = ""
        if block_handle["type"] != "paragraph":
            common_op.debug_log("paragraph type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return paragraph_ret
        return self.__text_list_parser(block_handle["paragraph"]["rich_text"], parser_type)

    # Page heading_1
    def heading_1_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        heading_1_ret = ""
        if block_handle["type"] != "heading_1":
            common_op.debug_log("heading_1 type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return heading_1_ret
        heading_1_ret = self.__text_list_parser(block_handle["heading_1"]["rich_text"], parser_type)
        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "# " + heading_1_ret
        else:
            return heading_1_ret

    # Page heading_2
    def heading_2_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        heading_2_ret = ""
        if block_handle["type"] != "heading_2":
            common_op.debug_log("heading_2 type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return heading_2_ret
        heading_2_ret = self.__text_list_parser(block_handle["heading_2"]["rich_text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "## " + heading_2_ret
        else:
            return heading_2_ret

    # Page heading_3
    def heading_3_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        heading_3_ret = ""
        if block_handle["type"] != "heading_3":
            common_op.debug_log("heading_3 type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return heading_3_ret
        heading_3_ret = self.__text_list_parser(block_handle["heading_3"]["rich_text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "### " + heading_3_ret
        else:
            return heading_3_ret

    # Page to_do
    def to_do_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        to_do_ret = ""
        if block_handle["type"] != "to_do":
            common_op.debug_log("to_do type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return to_do_ret
        to_do_ret = self.__text_list_parser(block_handle["to_do"]["rich_text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            if block_handle["to_do"]["checked"]:
                return "- [x] " + to_do_ret
            else:
                return "- [ ] " + to_do_ret
        else:
            return to_do_ret

    # Page bulleted_list_item
    def bulleted_list_item_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        bulleted_list_item_ret = ""
        if block_handle["type"] != "bulleted_list_item":
            common_op.debug_log(
                "bulleted_list_item type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                level=NotionDump.DUMP_MODE_DEFAULT)
            return bulleted_list_item_ret
        bulleted_list_item_ret = self.__text_list_parser(block_handle["bulleted_list_item"]["rich_text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "- " + bulleted_list_item_ret
        else:
            return bulleted_list_item_ret

    # Page numbered_list_item
    def numbered_list_item_parser(self, block_handle, list_index, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        numbered_list_item_ret = ""
        if block_handle["type"] != "numbered_list_item":
            common_op.debug_log(
                "numbered_list_item type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                level=NotionDump.DUMP_MODE_DEFAULT)
            return numbered_list_item_ret
        numbered_list_item_ret = self.__text_list_parser(block_handle["numbered_list_item"]["rich_text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return str(list_index) + ". " + numbered_list_item_ret
        else:
            return numbered_list_item_ret

    # Page toggle
    def toggle_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        toggle_ret = ""
        if block_handle["type"] != "toggle":
            common_op.debug_log("toggle type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return toggle_ret
        toggle_ret = self.__text_list_parser(block_handle["toggle"]["rich_text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "- " + toggle_ret
        else:
            return toggle_ret

    # Page divider
    def divider_parser(self, block_handle):
        divider_ret = ""
        if block_handle["type"] != "divider":
            common_op.debug_log("divider type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return divider_ret
        divider_ret = NotionDump.MD_DIVIDER
        return divider_ret

    # Page callout
    def callout_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        callout_ret = ""
        if block_handle["type"] != "callout":
            common_op.debug_log("callout type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return callout_ret
        callout_ret = self.__text_list_parser(block_handle["callout"]["rich_text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            # 这里是否每一行都操作
            return "> " + callout_ret
        else:
            return callout_ret

    # Page code
    def code_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        code_ret = ""
        if block_handle["type"] != "code":
            common_op.debug_log("code type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return code_ret
        code_ret = self.__text_list_parser(block_handle["code"]["rich_text"], parser_type)

        code_type = block_handle["code"]["language"]
        if code_type is None:
            code_type = ""

        if parser_type == NotionDump.PARSER_TYPE_MD:
            # 这里是否每一行都操作
            return "```" + code_type + "\n" + code_ret + "\n```"
        else:
            return code_ret

    # Page quote
    def quote_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        quote_ret = ""
        if block_handle["type"] != "quote":
            common_op.debug_log("quote type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return quote_ret
        quote_ret = self.__text_list_parser(block_handle["quote"]["rich_text"], parser_type)
        # 最外层颜色
        if block_handle["quote"]["color"] != "default":
            # 添加颜色，区分背景色和前景色
            if block_handle["quote"]["color"].find("_background") != -1:
                bg_color = block_handle["quote"]["color"][0:block_handle["quote"]["color"].rfind('_')]
                quote_ret = "<span style=\"background-color:" + color_transformer(bg_color, background=True) + "\">" + quote_ret + "</span>"
            else:
                quote_ret = "<font color=\"" + color_transformer(block_handle["quote"]["color"], background=False) + "\">" + quote_ret + "</font>"

        if parser_type == NotionDump.PARSER_TYPE_MD:
            # 这里是否每一行都操作
            return "> " + quote_ret
        else:
            return quote_ret

    # Page equation
    def equation_parser(self, block_handle):
        equation_ret = ""
        if block_handle["type"] != "equation":
            common_op.debug_log(" type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return equation_ret
        return self.__equation_block_parser(block_handle["equation"])

    # Page table_row
    def table_row_parser(self, block_handle, first_row=False, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        table_row_ret = ""
        if block_handle["type"] != "table_row":
            common_op.debug_log("table_row type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return table_row_ret

        table_row_list = self.__table_row_parser(block_handle, parser_type)
        table_row_ret = "|"
        for it in table_row_list:
            table_row_ret += it + "|"
        if first_row:
            table_row_ret += "\n|"
            for i in range(len(table_row_list)):
                table_row_ret += " --- " + "|"

        return table_row_ret

    def child_page_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        child_page_ret = ""
        if block_handle["type"] != "child_page":
            common_op.debug_log("child_page type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return child_page_ret

        page_body = block_handle["child_page"]
        if page_body["title"] == "":
            if parser_type == NotionDump.PARSER_TYPE_MD:
                return content_format.get_page_format_md("NULL Page", "NULL Page", export_child=self.export_child)
            else:
                return content_format.get_page_format_plain("NULL Page")
        else:
            page_id = (block_handle["id"]).replace('-', '')

            # 保存子页面信息
            common_op.debug_log("child_page_parser add page id = " + page_id, level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.add_new_child_page(self.child_pages, key_id=page_id, page_name=page_body["title"])

            if parser_type == NotionDump.PARSER_TYPE_MD:
                return content_format.get_page_format_md(page_id, page_body["title"], export_child=self.export_child)
            else:
                return content_format.get_page_format_plain(page_body["title"])

    # Page child_database
    def child_database_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "child_database":
            common_op.debug_log("child_database type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""

        # 子数据库保存在页面表中，不解析
        child_db_id = block_handle["id"].replace('-', '')
        common_op.add_new_child_page(
            self.child_pages,
            key_id=child_db_id,
            page_type="database",
            page_name=block_handle["child_database"]["title"]
        )
        common_op.debug_log(
            "child_database_parser add page id = " + child_db_id + "name : " + block_handle["child_database"]["title"], level=NotionDump.DUMP_MODE_DEFAULT)
        common_op.debug_log(internal_var.PAGE_DIC)
        common_op.debug_log("#############")
        common_op.debug_log(self.child_pages)

        # 子数据库要返回一个链接占位符，供后续解析使用
        if parser_type == NotionDump.PARSER_TYPE_MD:
            return content_format.get_page_format_md(
                child_db_id,
                block_handle["child_database"]["title"],
                export_child=self.export_child
            )
        else:
            return content_format.get_page_format_plain(block_handle["child_database"]["title"])

    # Page image
    def image_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "image":
            common_op.debug_log("image type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""

        # 子数据库保存在页面表中，不解析
        image_id = block_handle["id"].replace('-', '')
        image_name = self.__text_list_parser(block_handle["image"]["caption"], parser_type)
        image_url = ""
        image_type = block_handle["image"]["type"]
        if image_type in block_handle["image"].keys():
            if "url" in block_handle["image"][image_type].keys():
                image_url = block_handle["image"][image_type]["url"]
        if image_url == "":
            common_op.debug_log("unknown image type" + block_handle["image"]["type"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
        if image_name == "":
            # 如果文件没有名字使用id作为默认名字
            image_name = image_id
        common_op.add_new_child_page(
            self.child_pages,
            key_id=image_id,
            link_src=image_url,
            page_type="image",
            page_name=image_name
        )

        common_op.debug_log(
            "image_parser add page id = " + image_id + "name : " + image_name, level=NotionDump.DUMP_MODE_DEFAULT)
        common_op.debug_log(internal_var.PAGE_DIC)
        common_op.debug_log("#############")
        common_op.debug_log(self.child_pages)

        # 图片类型要返回一个链接占位符，供后续解析使用
        if parser_type == NotionDump.PARSER_TYPE_MD:
            return content_format.get_page_format_md(
                image_id,
                image_name,
                export_child=self.export_child
            )
        else:
            return content_format.get_page_format_plain(image_name)

    # Page file(file,pdf)
    def file_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "file" and block_handle["type"] != "pdf":
            common_op.debug_log("file type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""

        block_type = block_handle["type"]
        file_id = block_handle["id"].replace('-', '')
        file_name = self.__text_list_parser(block_handle[block_type]["caption"], parser_type)
        file_url = ""
        file_type = block_handle[block_type]["type"]
        if file_type in block_handle[block_type].keys():
            if "url" in block_handle[block_type][file_type].keys():
                file_url = block_handle[block_type][file_type]["url"]
        if file_url == "":
            common_op.debug_log("unknown block type" + block_handle[block_type]["type"] + " with null url",
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        # 如果caption中没有文件名，尝试从url中分离
        if file_name == "":
            file_url_basic = file_url[0:file_url.rfind('?')]
            file_name = file_url_basic[file_url_basic.rfind('/')+1:]
            # url中分离的内容需要转码
            file_name = unquote(file_name, 'utf-8')
        if file_name == "":
            # 如果文件没有名字使用id作为默认名字
            file_name = file_id
        common_op.add_new_child_page(
            self.child_pages,
            key_id=file_id,
            link_src=file_url,
            page_type="file",
            page_name=file_name
        )

        common_op.debug_log(
            "file_parser add page id = " + file_id + " name : " + file_name, level=NotionDump.DUMP_MODE_DEFAULT)
        common_op.debug_log(internal_var.PAGE_DIC)
        common_op.debug_log("#############")
        common_op.debug_log(self.child_pages)

        # 文件类型要返回一个链接占位符，供后续解析使用
        if parser_type == NotionDump.PARSER_TYPE_MD:
            return content_format.get_page_format_md(
                file_id,
                file_name,
                export_child=self.export_child
            )
        else:
            return content_format.get_page_format_plain(file_name)

    # Page bookmark
    def bookmark_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        bookmark_ret = ""
        if block_handle["type"] != "bookmark":
            common_op.debug_log("bookmark type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return bookmark_ret
        bookmark_name = self.__text_list_parser(block_handle["bookmark"]["caption"], parser_type)
        if bookmark_name == "":
            bookmark_name = block_handle["id"]
        bookmark_url = block_handle["bookmark"]["url"]

        # bookmark 类型要返回一个链接占位符，供后续解析使用
        if parser_type == NotionDump.PARSER_TYPE_MD:
            # file转换成文件链接的形式
            return content_format.get_file_format_md(bookmark_name, bookmark_url)
        else:
            return content_format.get_file_format_plain(bookmark_name, bookmark_url)

    # Page link_preview
    def link_preview_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        link_preview_ret = ""
        if block_handle["type"] != "link_preview":
            common_op.debug_log("link_preview type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return link_preview_ret
        link_preview_name = "LINK_PREVIEW"
        link_preview_url = block_handle["link_preview"]["url"]

        # bookmark 类型要返回一个链接占位符，供后续解析使用
        if parser_type == NotionDump.PARSER_TYPE_MD:
            # file转换成文件链接的形式
            return content_format.get_file_format_md(link_preview_name, link_preview_url)
        else:
            return content_format.get_file_format_plain(link_preview_name, link_preview_url)

    # Page link_to_page
    def link_to_page_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        link_to_page_ret = ""
        if block_handle["type"] != "link_to_page":
            common_op.debug_log("link_to_page type error! parent_id= " + self.base_id + " id= " + block_handle["id"],
                                level=NotionDump.DUMP_MODE_DEFAULT)
            return link_to_page_ret

        link_page = block_handle["link_to_page"]
        if link_page["type"] == "page_id":
            page_id = link_page["page_id"].replace('-', '')
            page_name = ""
            key_id = page_id + "_link_page"
            common_op.add_new_child_page(
                self.child_pages,
                key_id=key_id,
                link_id=page_id,
                page_type="page",
                page_name=page_name
            )
            common_op.debug_log(
                "link_to_page_parser add link_page key_id = " + key_id, level=NotionDump.DUMP_MODE_DEFAULT)
            common_op.debug_log(internal_var.PAGE_DIC)
            common_op.debug_log("#############")
            common_op.debug_log(self.child_pages)
            return content_format.get_page_format_md(
                key_id,
                page_name,
                export_child=self.export_child
            )
        else:
            common_op.debug_log("unknown type " + link_page["type"], level=NotionDump.DUMP_MODE_DEFAULT)
        return link_to_page_ret
