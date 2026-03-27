---
name: windows-privilege-escalation
description: Windows 本地提权与权限提升排查要点（服务/策略/凭证/委派）
version: 1.0.0
---

# Windows 提权（本地/域内）排查要点

## 适用场景
- 已获得 Windows 目标的低权限执行/交互（WebShell、远程命令、RDP/WinRM 等）
- 需要从普通用户提升到本地管理员，或从域用户提升到更高权限
- 需要输出可复现的证据链与修复建议

## 安全与证据原则
- 优先“只读枚举”，避免破坏性操作与持久化
- 不在报告正文记录明文口令；对哈希/票据按策略脱敏
- 每一步明确：前提、动作、结果、证据

## 1) 基础信息收集（低噪声）
```powershell
whoami
whoami /groups
whoami /priv
hostname
systeminfo
ipconfig /all
```

补充：补丁与版本（用于判断已知提权面）：
```powershell
wmic qfe get HotFixID,InstalledOn,Description
```

## 2) 自动化检查（推荐先跑，后人工验证）
- winPEAS（常见误报较多，需人工复核）
- Seatbelt（偏系统态信息与策略）
- PowerUp（服务/权限类点位）

建议输出：仅保留“命中项 + 证据行”，避免把大量无关输出塞进对话/报告。

## 3) 服务与任务（最常见提权来源）

### 3.1 服务可执行文件/目录权限
目标：识别服务二进制或其目录是否被低权限用户可写。

```powershell
sc query state= all
wmic service get Name,StartName,PathName
```

关注点：
- 可写的 `PathName` 目录（例如 `C:\Program Files\Vendor\` 被 Users 可写）
- 服务运行账户是 `LocalSystem`/管理员

### 3.2 未加引号的服务路径（Unquoted Service Path）
```powershell
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "\""
```
命中后需要验证：路径是否包含空格、可投放位置是否可写、服务是否可重启。

### 3.3 计划任务（Task Scheduler）
```powershell
schtasks /query /fo LIST /v
```
关注点：任务可执行文件位置、触发条件、运行账户、是否可由低权限用户修改。

## 4) 关键策略与配置缺陷

### 4.1 AlwaysInstallElevated
```powershell
reg query HKCU\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```
若两者都为 1，需要评估 MSI 安装链的风险与修复建议。

### 4.2 UAC 与本地组成员
```powershell
net localgroup administrators
```
若已在本地管理员组但受 UAC 限制，需按环境评估可用的提权方式与审计证据。

## 5) 凭证线索（只读优先）
常见泄露位置：
- 共享目录/脚本（部署脚本、备份脚本、CI/CD 配置）
- 配置文件（Web 配置、数据库连接串、RMM 工具配置）
- 计划任务参数、服务命令行参数

本机线索：
```powershell
cmdkey /list
dir C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ /s
```

## 6) 域内场景（从本地到域）
- 如果当前机器是域成员：优先确认是否存在“可复用凭证”（服务账号、登录会话、脚本凭证）
- 如果可访问域控/LDAP：结合 AD 路径分析（ACL/委派/票据攻击）规划下一步

## 7) 报告输出建议
- 命中项分类：服务/任务、策略、凭证泄露、域路径
- 每条漏洞写清：影响、利用前提、复现步骤、证据、修复建议
- 修复建议重点：收敛写权限、最小权限服务账户、关闭危险策略、加强凭证管理与审计

