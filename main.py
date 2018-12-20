# -*- coding: utf-8 -*-
import os
import sys
from time import time

from pyepub import EPUB

filename = sys.argv[1]

# 加载ePub文件
epub = EPUB(filename)

# EPUB对象属性
sha1 = epub.sha1            # ePub文件SHA-1(str)
nav = epub.nav              # ePub目录(list)
nav_point = epub.nav_point  # ePub章节(dict)
items = epub.items          # ePub文件(dict)
metadata = epub.metadata    # ePub元数据(dict)

# 遍历ePub元数据(可用epub[name]快速访问)
for name, data in metadata.items():
    print("%s:" % name.capitalize(), data)

# 获取ePub文件内资源
cover = epub.get_file(epub["cover"])

# 转换至mobi格式
t = time()
with open(os.path.splitext(filename)[0] + ".mobi", "wb") as file:
    file.write(epub.convert_to_mobi())
t1 = time() - t
print("'mobi' file has been saved to '%s'[%.2fs]" % (os.path.splitext(filename)[0] + ".mobi", t1))

# 转换至txt格式
t = time()
with open(os.path.splitext(filename)[0] + ".txt", "wb") as file:
    file.write(epub.convert_to_txt().encode("utf-8"))
t2 = time() - t
print("'txt' file has been saved to '%s'[%.2fs]" % (os.path.splitext(filename)[0] + ".txt", t2))

