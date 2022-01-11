# notion-dump-kernel

## Description

This Repo is a development based on notion-client（notion official API），and main targets are

- [x] Export Notion Database(Table) as a csv file
- [x] Export Notion Page or Block as md file
- [x] Recursion Export child Page or Database(Table)  in Page
- [x] Recursion Export child Page in Database(Table) （All in all，all can Recursion Export）
- [ ] Export Notion Page as SQL
- [ ] Export  SQL as md&CSV file

## Structure

```shell
notoin-dump
├─NotionDump
│  ├─Dump   # External Interface
│  ├─Notion # Unified encapsulation interface for communication with Notion
│  ├─Parser # Some parser
│  ├─SQL    # About SQL, TODO
│  └─utils  # Internal variables and utils functions
└─Tests 	# Test code
```



## Usage

### 3.0 install & import

**install `notion-dump-kernel`**

```powershell
# open terminal, type the cmd (stable version is 0.0.3)
pip install notion-dump-kernel
# or
pip install notion-dump-kernel==0.0.3
```

**import**

```python
import NotionDump
from NotionDump.Dump.dump import Dump
from NotionDump.Notion.Notion import NotionQuery
```



### 3.1 API

```python
# Get notion query handle
query_handle = NotionQuery(
    token=TOKEN_TEST,                  # Token
    client_handle=None,                # Notion official API handle, default is None(use token is OK)
    async_api=False                    # async, default is False
)

# Get dump handle 
handle = Dump(
    dump_id=ID,                        # the ID which need to export (block, page or database)
    query_handle=query,                # Notion query handle (NOT the offical API handle)
    export_child_pages=True, 		   # Recursion export child page 
    dump_type=NotionDump.DUMP_TYPE_XXX # ID type, see the descriptions below
)

# dump type ( dump_type )
DUMP_TYPE_BLOCK						   # Block type
DUMP_TYPE_PAGE						   # Page type
DUMP_TYPE_DB_TABLE                     # Database table type

# Other
# the varible itself shows all
```



### 3.2 Get output

The result of dump save at a dictionary variable , which contain all info about dumped files. The explain of output shows below.

```python
# Get output
dump_output = dump_handle.dump_to_file()
# dump_handle is the return value of Dump(xxx)
```

```json
// output explain
// output is a dictionary variable, key is id (block id/page id/database id)
{
    "id_1": {
        "dumped": true,			          // download status of the resource specifid by id
        "main_page": true,		          // whether the page is the page specifid by input id (root)
        "page_recursion": true,           // internal variable(NOT use)
        "type": "page",                   // root id type, database or page (page type contain page and block)
        "local_path": "xxxx.md/xxxx.csv", // the location of export file, for subsequent operations
        "page_name": "",                  // page name (for subsequent relocation of page url)
        "child_pages": [
            "child_id",                   // subpage or database id this key_id contain
            "child_id"
        ]
    },
    "id_2": {
        "dumped": true,			          
        "main_page": true,		          
        "page_recursion": true,           
        "type": "page",                   
        "local_path": "xxxx.md/xxxx.csv", 
        "page_name": "",                  
        "child_pages": []
    }
}
```



## TODO

### 4.1 Export to SQL

Plan: All page save in one table, and every csv file save as a table

*My SQL skills is very weak*



## Attention

**Problem**

- [ ] Comment can't export
- [ ] the csv file lost it's format shows in notion client



## Others

### Notion Test Page

[Notion Test Page](https://delta1037.notion.site/Notion-dump-ed0a3b0f57b34712bc6bafcbdb413d50)

