# 技能：查阅 Kali Linux 官方工具文档

## 描述
当遇到不熟悉的工具，或者需要查找特定工具的高级用法（如生僻参数、特定场景的 Flag）时，应优先查阅 Kali Linux 官方工具文档。

## 执行步骤

1.  **确定工具名称**: 明确你正在使用的工具名称（例如 `wfuzz`, `gobuster`, `impacket`）。
2.  **构造搜索查询**: 使用 `web_search` 工具，限定搜索范围为 `kali.org/tools`。
    *   查询模板: `site:kali.org/tools {tool_name} usage examples`
3.  **分析搜索结果**:
    *   点击标题包含工具名称的链接（通常是 `https://www.kali.org/tools/{tool_name}/`）。
    *   **阅读 Synopsis**: 了解工具的基本功能。
    *   **查看 Options**: 查找你需要的具体参数（如设置超时、代理、线程数等）。
    *   **学习 Examples**: 官方文档通常在底部提供非常实用的命令行示例，直接参考这些示例可以避免语法错误。
4.  **应用知识**: 将查到的参数应用到当前的 `ToolExecutor` 命令中。

## 示例场景
**场景**: 你需要使用 `hydra` 对 RDP 服务进行爆破，但忘记了 RDP 模块的特定参数。
**行动**:
1. 调用 `web_search(query="site:kali.org/tools hydra rdp example")`。
2. 阅读结果，找到 `rdp://` 协议的使用格式。
3. 构造命令: `hydra -L users.txt -P pass.txt rdp://192.168.1.5`。
