# notion-dump

[English_Version](https://github.com/delta1037/notion-dump/blob/main/README_En.md)

------

## 说明

本仓库是基于notion-client的开发，主要实现目标有

- [x] 将Notion数据库导出为CSV文件
- [ ] 将Notion Page页面导出为md文件
- [ ] 将Notion Page页面导出到数据库（SQL）
- [ ] 将数据库（SQL）导出成md&CSV文件

## 项目结构

```shell
notoin-dump
├─NotionDump
│  ├─Api    # 与Notion通信
│  └─Parser # 解析Json数据
└─Tests 	# 测试代码
```

## 输出文件结构

### Page导出结构

Page导出需要Page id和一些必要的认证信息

-   Page主页（Page id指定的所有的页面）
    -   sub_page（除Page id所有的子页面或者子子页面）
    -   database（页面中的数据库）

### 数据库导出结构

数据库导出是将所有的page存储到一张表里，将导出的每一个CSV文件作为一张表存储

我数据库不太行，只能想到这样的存储方法

## Attention

需要完善的内容
- [x] 段落中的链接
- [x] 文件链接 
- [ ] 文件内的表格Table
- [ ] 数据库CSV只是存了下来，但是本地查看因为没有格式极其不方便
- [ ] page和CSV存储到SQL数据库

需要深层解析的内容
- [x] 各种列表
- [ ] page页面
- [ ] page中的数据库文件，作为一个文件链接存在即可

已知的问题
- [ ] 评论内容无法获取到
- [ ]
