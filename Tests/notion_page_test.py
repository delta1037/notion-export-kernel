from NotionDump.Api.page import Page
from NotionDump.utils import common_op

TOKEN_TEST = "secret_WRLJ9xyEawNxzRhVHVWfciTl9FAyNCd29GMUvr2hQD4"
PAGE_MIX_ID = "950e57e0507b4448a55a13b2f47f031f"


# 获取数据库原始数据测试：根据token和id获取json数据，得到临时JSON文件
def test_get_page_json_data():
    page_handle = Page(token=TOKEN_TEST, page_id=PAGE_MIX_ID)
    page_handle.page_to_json()


# 解析数据库内容测试：根据token和id解析数据库内容，得到临时CSV文件
def test_page_parser():
    page_handle = Page(token=TOKEN_TEST, page_id=PAGE_MIX_ID, export_child_pages=True)
    page_handle.page_to_md()

    # 输出样例
    page_detail_json = page_handle.get_pages_detail()
    common_op.save_json_to_file(page_detail_json, "page_detail.json")


if __name__ == '__main__':
    # 获取数据库原始数据测试
    test_get_page_json_data()

    # 解析数据库内容测试
    test_page_parser()
