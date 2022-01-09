# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import string
import logging
import NotionDump


class BlockParser:
    def __init__(self, block_id):
        self.block_id = block_id

    # 讲Text块，Json格式获取到纯文本(去除格式)
    def __text_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "text":
            logging.exception("text type error! id=" + self.block_id)
            print(block_handle)
            return ""
        text_str = block_handle["plain_text"]
        return text_str

    def __text_block_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        paragraph_ret = ""
        if block_handle["type"] == "text":
            paragraph_ret = self.__text_parser(block_handle)
        elif block_handle["type"] == "equation":
            paragraph_ret = self.__equation_inline_parser(block_handle)
        elif block_handle["type"] == "mention":
            paragraph_ret = self.__mention_parser(block_handle)
        else:
            logging.exception("text type error! parent_id= " + self.block_id)
        return paragraph_ret

    def __text_list_parser(self, text_list, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        plain_text = ""
        if text_list is not None:
            for text_block in text_list:
                plain_text += self.__text_block_parser(text_block, parser_type)
        return plain_text

    def __people_parser(self, block_handle):
        if block_handle["object"] != "user":
            logging.exception("people type error! id=" + self.block_id)
            return ""
        # 优先获取名字
        if block_handle["name"] is not None:
            return block_handle["name"]
        # 如果无法获取名字则返回id
        return block_handle["id"]

    def __user_parser(self, block_handle):
        if block_handle["type"] != "user":
            logging.exception("user type error! id=" + self.block_id)
            return ""
        user_body = block_handle["user"]
        return self.__people_parser(user_body)

    def __file_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "file":
            logging.exception("file type error! id=" + self.block_id)
            return ""
        filename = block_handle["name"]
        file_url = block_handle["file"]["url"]
        # 格式处理简单格式（也可以转换成markdown格式[]()）
        return filename + "|" + file_url

    # "$ equation_inline $"
    def __equation_inline_parser(self, block_handle):
        if block_handle["type"] != "equation":
            logging.exception("equation inline type error! id=" + self.block_id)
            return ""
        eq_str = "$ " + block_handle["plain_text"] + " $"
        return eq_str

    # "$$ equation_inline $$"
    def __equation_block_parser(self, block_handle):
        if block_handle["expression"] is None:
            logging.exception("equation block no expression! id=" + self.block_id)
            return ""
        eq_str = "$$ " + block_handle["expression"] + " $$"
        return eq_str

    # 关于链接到其它的Page可能需要递归处理
    def __page_parser(self, block_handle):
        if block_handle["type"] != "page":
            logging.exception("page type error! parent_id= " + self.block_id)
            return ""

        page_body = block_handle["page"]
        return page_body["id"]

    # 提及到其它页面，日期，用户
    def __mention_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "mention":
            logging.exception("mention type error! parent_id= " + self.block_id)
            return ""

        mention_body = block_handle["mention"]
        if mention_body["type"] == "date":
            return self.date_parser(mention_body)
        elif mention_body["type"] == "user":
            return self.__user_parser(mention_body)
        elif mention_body["type"] == "page":
            return self.__page_parser(mention_body)

    # 数据库 title
    def title_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "title":
            logging.exception("title type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        return self.__text_list_parser(block_handle["title"], parser_type)

    # 数据库 rich_text
    def rich_text_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "rich_text":
            logging.exception("rich_text type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        return self.__text_list_parser(block_handle["rich_text"], parser_type)

    # 数据库 multi_select
    def multi_select_parser(self, block_handle):
        if block_handle["type"] != "multi_select":
            logging.exception("multi_select type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        multi_select_list = block_handle["multi_select"]
        ret_str = ""
        if multi_select_list is None:
            return ret_str
        for multi_select in multi_select_list:
            if ret_str != "":
                ret_str += ","  # 多个选项之间用“,”分割
            ret_str += multi_select["name"]
        return ret_str

    # 数据库 select
    def select_parser(self, block_handle):
        if block_handle["type"] != "select":
            logging.exception("select type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        select = block_handle["select"]
        ret_str = ""
        if select is None:
            return ret_str
        ret_str = select["name"]
        return ret_str

    # 数据库 url
    def url_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        if block_handle["type"] != "url":
            logging.exception("url type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        url = block_handle["url"]
        # print(url)
        ret_str = ""
        if url is not None:
            ret_str = url
        return ret_str

    # 数据库 email
    def email_parser(self, block_handle):
        if block_handle["type"] != "email":
            logging.exception("email type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        email = block_handle["email"]
        # print(email)
        ret_str = ""
        if email is not None:
            ret_str = email
        return ret_str

    # 数据库 checkbox
    def checkbox_parser(self, block_handle):
        if block_handle["type"] != "checkbox":
            logging.exception("checkbox type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        checkbox = block_handle["checkbox"]
        # print(email)
        ret_str = ""
        if checkbox is True:
            ret_str = "true"
        else:
            ret_str = "false"
        return ret_str

    # 数据库 phone_number
    def phone_number_parser(self, block_handle):
        if block_handle["type"] != "phone_number":
            logging.exception("phone_number type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        phone_number = block_handle["phone_number"]
        # print(email)
        ret_str = ""
        if phone_number is not None:
            ret_str = phone_number
        return ret_str

    # 数据库 date
    def date_parser(self, block_handle):
        if block_handle["type"] != "date":
            logging.exception("date type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        date = block_handle["date"]
        # print(date)
        ret_str = ""
        if date is None:
            return ret_str

        if date["start"] is not None:
            ret_str = date["start"]
        if date["end"] is not None:
            ret_str += " ~ " + date["end"]  # 日期之间用“~”分割
        return ret_str

    # 数据库 people
    def people_parser(self, block_handle):
        if block_handle["type"] != "people":
            logging.exception("people type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
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
            logging.exception("number type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
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
            logging.exception("files type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return ""
        files_list = block_handle["files"]
        ret_str = ""
        if files_list is None:
            return ret_str
        for file in files_list:
            if ret_str != "":
                ret_str += ","  # 多个文件之间用“,”分割
            ret_str += self.__file_parser(file, parser_type)
        return ret_str

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
            logging.exception("paragraph type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return paragraph_ret
        return self.__text_list_parser(block_handle["paragraph"]["text"], parser_type)

    # Page heading_1
    def heading_1_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        heading_1_ret = ""
        if block_handle["type"] != "heading_1":
            logging.exception("heading_1 type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return heading_1_ret
        heading_1_ret = self.__text_list_parser(block_handle["heading_1"]["text"], parser_type)
        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "# " + heading_1_ret
        else:
            return heading_1_ret

    # Page heading_2
    def heading_2_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        heading_2_ret = ""
        if block_handle["type"] != "heading_2":
            logging.exception("heading_2 type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return heading_2_ret
        heading_2_ret = self.__text_list_parser(block_handle["heading_2"]["text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "## " + heading_2_ret
        else:
            return heading_2_ret

    # Page heading_3
    def heading_3_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        heading_3_ret = ""
        if block_handle["type"] != "heading_3":
            logging.exception("heading_3 type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return heading_3_ret
        heading_3_ret = self.__text_list_parser(block_handle["heading_3"]["text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "### " + heading_3_ret
        else:
            return heading_3_ret

    # Page to_do
    def to_do_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        to_do_ret = ""
        if block_handle["type"] != "to_do":
            logging.exception("to_do type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return to_do_ret
        to_do_ret = self.__text_list_parser(block_handle["to_do"]["text"], parser_type)

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
            logging.exception(
                "bulleted_list_item type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return bulleted_list_item_ret
        bulleted_list_item_ret = self.__text_list_parser(block_handle["bulleted_list_item"]["text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "- " + bulleted_list_item_ret
        else:
            return bulleted_list_item_ret

    # Page numbered_list_item
    def numbered_list_item_parser(self, block_handle, list_index, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        numbered_list_item_ret = ""
        if block_handle["type"] != "numbered_list_item":
            logging.exception(
                "numbered_list_item type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return numbered_list_item_ret
        numbered_list_item_ret = self.__text_list_parser(block_handle["numbered_list_item"]["text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return str(list_index) + ". " + numbered_list_item_ret
        else:
            return numbered_list_item_ret

    # Page toggle
    def toggle_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        toggle_ret = ""
        if block_handle["type"] != "toggle":
            logging.exception("toggle type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return toggle_ret
        toggle_ret = self.__text_list_parser(block_handle["toggle"]["text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            return "- " + toggle_ret
        else:
            return toggle_ret

    # Page divider
    def divider_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        divider_ret = ""
        if block_handle["type"] != "divider":
            logging.exception("divider type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return divider_ret
        divider_ret = NotionDump.MD_DIVIDER
        return divider_ret

    # Page callout
    def callout_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        callout_ret = ""
        if block_handle["type"] != "callout":
            logging.exception("callout type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return callout_ret
        callout_ret = self.__text_list_parser(block_handle["callout"]["text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            # 这里是否每一行都操作
            return "> " + callout_ret
        else:
            return callout_ret

    # Page code
    def code_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        code_ret = ""
        if block_handle["type"] != "code":
            logging.exception("code type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return code_ret
        code_ret = self.__text_list_parser(block_handle["code"]["text"], parser_type)

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
            logging.exception("quote type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return quote_ret
        quote_ret = self.__text_list_parser(block_handle["quote"]["text"], parser_type)

        if parser_type == NotionDump.PARSER_TYPE_MD:
            # 这里是否每一行都操作
            return "> " + quote_ret
        else:
            return quote_ret

    # Page equation
    def equation_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        equation_ret = ""
        if block_handle["type"] != "equation":
            logging.exception(" type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return equation_ret
        return self.__equation_block_parser(block_handle["equation"])

    # Page table # TODO
    def table_parser(self, block_handle, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        table_ret = ""
        if block_handle["type"] != "table":
            logging.exception("table type error! parent_id= " + self.block_id + " id= " + block_handle["id"])
            return table_ret
        return ""
