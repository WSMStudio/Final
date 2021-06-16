# 最终材料

存放最终上交的演示程序和报告

## 使用方法
首先建立索引
```text
Python build_index_meta.py
Python build_index_content.py
```
然后开启服务器
```text
Python server.py
```
然后在浏览器中访问
```text
localhost:8000
```
## 测试样例

+ Boolean Search
```text
content: christmas
content: christmas and content: story
content: [christmas /1 story]
content: [christmas /3 story]
content: [christmas PRE/3 story]
content: [christmas PRE/5 story]
content: christmas and content: [snow /4 fall]
content: christmas and content: [snow /4 fall] or year: 2008
content: christmas and (content: [snow /4 fall] or year: 2008)
content: christmas and content: [snow /4 fall] and year: 2008
content: christmas and not content: snow
```

+ Mis-spelling
```text
content: hllo
content: respnsonse
content: hllo and content: wrld
```

+ Wild-card
```text
title: "Declar*"
title: "Indepen*"
title: "*ternet"
year: "20*8"
year: "*76"
author: "Jame*"
author: "jeffer*"
author: "*rick"
content: "with*"
content: "state*"
content: "*end"
content: "de*end"
content: "*ith*"
```