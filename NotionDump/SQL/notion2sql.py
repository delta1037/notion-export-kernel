# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

# 将md文件和CSV文件写入到数据库
class Notion2SQL:
    def __init__(self, db_connect):
        self.db_connect = db_connect
