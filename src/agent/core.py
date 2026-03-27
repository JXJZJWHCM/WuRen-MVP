import os
import json
import logging
import asyncio
import re
import httpx
from src.utils.web_searcher import WebSearcher
from src.utils.rag_engine import RAGEngine
from src.utils.knowledge_graph import KnowledgeGraph
from openai import OpenAI
from typing import List, Dict, Any
from src.tools.manager import ToolManager
from src.tools.executor import ToolExecutor
from src.utils.network import get_ip_address, get_default_interface_name, get_primary_ipv4

logger = logging.getLogger(__name__)

class PentestAgent:
    def __init__(self, tool_manager: ToolManager, executor: ToolExecutor, model="deepseek-reasoner", base_dir: str = None):
        # Configure custom HTTP client for interface binding
        forced_lhost = os.getenv("AI_LHOST")
        bind_interface = os.getenv("AI_BIND_INTERFACE") or get_default_interface_name() or "eth0"
        local_address = None
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Try to get IP from interface name
        if forced_lhost:
            self.lhost = forced_lhost
            logger.info(f"Using forced AI_LHOST={forced_lhost}")
        elif bind_interface:
            ip = get_ip_address(bind_interface)
            if ip:
                local_address = ip
                logger.info(f"Binding AI traffic to interface {bind_interface} ({ip})")
                # Inject LHOST into system prompt
                self.lhost = ip
            else:
                fallback_ip = get_primary_ipv4()
                if fallback_ip:
                    local_address = fallback_ip
                    logger.warning(f"Could not find IP for interface {bind_interface}, falling back to {fallback_ip}")
                    self.lhost = fallback_ip
                else:
                    logger.warning(f"Could not find IP for interface {bind_interface}, falling back to 127.0.0.1")
                    self.lhost = "127.0.0.1"
        else:
             self.lhost = "127.0.0.1"

        # Create transport with local_address binding if available
        # Relaxed timeout for AI thinking (300 seconds)
        timeout = httpx.Timeout(300.0, connect=60.0)
        transport = httpx.HTTPTransport(local_address=local_address) if local_address else None
        proxy_url = (os.getenv("PROXY_URL") or "").strip()
        client_kwargs = {"timeout": timeout}
        if proxy_url:
            client_kwargs["proxy"] = proxy_url
        if transport:
            client_kwargs["transport"] = transport
        http_client = httpx.Client(**client_kwargs)

        provider = os.getenv("AI_PROVIDER", "deepseek")
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        else:
            api_key = os.getenv("DEEPSEEK_API_KEY", "sk-placeholder")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

        self.ai_provider = provider
        self.ai_base_url = base_url
        self.client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        self.tool_manager = tool_manager
        self.executor = executor
        self.model = os.getenv("AI_MODEL") or model
        self.messages = []
        self.task_id = None
        self.vuln_store = None
        
        # Initialize RAG Engine & Knowledge Graph
        self.rag_engine = RAGEngine(
            persist_directory=os.path.join(self.base_dir, "data", "vector_db"),
            cache_directory=os.path.join(self.base_dir, "data", "models"),
        )
        self.knowledge_graph = KnowledgeGraph(persist_path=os.path.join(self.base_dir, "data", "knowledge_graph", "graph.json"))
        
        # MOE Experts Configuration
        self.experts = {
            "Reconnaissance": {
                "system_prompt": "你是一个信息收集专家 (Recon Expert)。专注于使用 Nmap, Web指纹识别, DNS 枚举等工具。你的目标是尽可能多地发现目标资产、端口、服务版本和潜在入口点。不要尝试进行漏洞利用。",
                "allowed_tools": [
                    "amass",
                    "arp-scan",
                    "dnsenum",
                    "dirb",
                    "dirsearch",
                    "feroxbuster",
                    "ffuf",
                    "fierce",
                    "gau",
                    "gobuster",
                    "hakrawler",
                    "katana",
                    "masscan",
                    "nbtscan",
                    "nikto",
                    "nmap",
                    "nmap-advanced",
                    "rustscan",
                    "subfinder",
                    "wafw00f",
                    "web_screenshot",
                    "ocr_image",
                    "exec",
                ],
            },
            "Exploitation": {
                "system_prompt": "你是一个漏洞验证专家 (Vulnerability Validation Expert)。基于已收集信息，优先用低影响方式验证漏洞是否存在，并形成可复核证据与修复建议。必要时可检索公开资料与漏洞库，但不要生成/输出可直接执行的利用脚本、载荷或持久化内容；对生产环境保持保守。",
                "allowed_tools": [
                    "dalfox",
                    "hydra",
                    "jaeles",
                    "msfconsole",
                    "msfvenom",
                    "nuclei",
                    "searchsploit",
                    "sqlmap",
                    "wfuzz",
                    "wpscan",
                    "xsser",
                    "web_screenshot",
                    "ocr_image",
                    "exec",
                ],
            },
            "Persistence": {
                "system_prompt": "你是一个权限与暴露面评估专家 (Privilege & Exposure Assessment Expert)。仅在明确授权且不影响业务的前提下，验证权限边界、配置风险与潜在扩散路径，并形成证据与修复建议。不要部署后门、不要进行持久化操作。",
                "allowed_tools": [
                    "bloodhound",
                    "impacket",
                    "linpeas",
                    "msfconsole",
                    "ncat",
                    "netexec",
                    "rpcclient",
                    "ssh",
                    "web_screenshot",
                    "ocr_image",
                    "exec",
                ],
            },
            "Lateral Movement": {
                "system_prompt": "你是一个内网风险评估专家 (Internal Network Risk Assessment Expert)。仅在明确授权范围内评估内网暴露面、信任关系与潜在风险扩散路径，输出可复核证据与加固建议。不要进行越权扩散行为。",
                "allowed_tools": [
                    "arp-scan",
                    "bloodhound",
                    "impacket",
                    "nmap",
                    "nmap-advanced",
                    "ncat",
                    "netexec",
                    "responder",
                    "rpcclient",
                    "smbmap",
                    "ssh",
                    "exec",
                ],
            },
            "Report": {
                "system_prompt": "你是一个报告生成专家。汇总所有阶段的发现，生成一份结构清晰、证据确凿的渗透测试报告。",
                "allowed_tools": ["list-files", "ocr_image"],
            },
            "Code Audit": {
                "system_prompt": "你是一个代码审计专家 (Code Audit Expert)。你负责对源代码与配置进行安全审计：识别认证/鉴权/输入校验/权限控制/加密使用/密钥管理/敏感信息泄露等问题，并给出可落地的修复建议与可复现的证据定位。避免提供可直接用于攻击的利用代码。",
                "allowed_tools": [
                    "list-files",
                    "cat",
                    "exec",
                    "code_audit",
                ],
            },
            "Reverse Engineering": {
                "system_prompt": "你是一个逆向与二进制分析专家 (Reverse Engineering Expert)。你负责对二进制/固件/样本进行快速体检与静态分析，提取关键字符串、编译安全特性、段/符号信息、嵌入资源与潜在线索，并给出下一步分析路径。避免生成或保存可直接攻击的武器化载荷。",
                "allowed_tools": [
                    "binary_triage",
                    "binwalk",
                    "checksec",
                    "exiftool",
                    "foremost",
                    "gdb",
                    "ghidra",
                    "objdump",
                    "radare2",
                    "strings",
                    "xxd",
                    "exec",
                ],
            },
        }
        self.current_phase = "Reconnaissance"

        # Note: Indexing should be done on startup or on-demand, not blocking init.
        # We will lazy-load it when search_knowledge is called or via separate task.
        
        # Load Tool Instructions
        instruction_path = os.path.join(self.base_dir, "config", "tool_instructions.md")
        tool_instructions = ""
        if os.path.exists(instruction_path):
            with open(instruction_path, "r", encoding="utf-8") as f:
                tool_instructions = f.read()

        self.system_prompt = f"""你是一个自动化的安全评估代理。
你的目标是在合法合规、明确授权与边界控制的前提下，对指定目标执行可审计、可复核的安全评估与交付。
默认流程为：信息收集 -> 漏洞验证 -> 报告交付。仅当任务目标明确要求且已获得授权时，才进入更深入的权限/内网风险评估阶段。
当任务目标明确包含“代码审计/安全评审”或提供了源码仓库/配置文件时，可切换到 Code Audit 阶段；当任务目标包含“逆向/样本分析”或提供二进制/固件样本时，可切换到 Reverse Engineering 阶段。

**通用推理与行动原则 (General Reasoning & Action)**：
1. **观察 (Observe)**: 读取用户目标、网络环境、以及每一次工具输出（stdout/stderr/return_code）。从“端口/协议/服务/版本/配置/错误信息/默认凭证迹象”提取事实。
2. **建模 (Orient)**: 用事实建立目标画像与攻击面列表：可达面、认证面、输入面、文件面、管理面、内网面。不要把单一结果当结论，优先用交叉验证降低误报。
3. **决策 (Decide)**: 从“最小风险、最高信息增益”开始，逐步推进：探测/枚举 → 验证/复现 → 证据固化 → 修复建议与复测。工具与漏洞都按场景选择，不固化某一个工具或某一个漏洞模板。
4. **执行 (Act)**: 每步只做一件事，参数可解释、输出可复现。失败时先根据报错修正输入与假设，再重试不同路径，避免重复执行完全相同的命令。
5. **安全与证据 (Safety & Evidence)**:
   - 默认避免破坏性操作；任何可能造成数据破坏/服务中断的动作，优先选择只读验证方式或轻量级 PoC。
   - 发现关键页面/后台/敏感信息/成功利用时，必须截图取证并在后续报告引用。
   - 当你“确认漏洞成立”（已验证证据闭环）时，必须调用 `register_vulnerability` 登记漏洞要点（原理/证据/影响/修复），用于漏洞管理与报告跟踪；不要写入可直接复制执行的利用脚本或持久化载荷。
6. **知识增强 (Knowledge Augmentation)**:
   - 不确定原理/利用链/工具用法时，先 `search_knowledge`，不足再 `web_search`。
   - 学到可复用的技巧/参数/排错方法，用 `add_knowledge` 固化为知识条目。

**服务与入口的通用验证策略**:
- **网络服务**: 先完成端口与协议识别，再做面向协议的枚举与脚本检测。
- **Web/HTTP**: 先确定站点边界（虚拟主机/路径/参数/API），再做目录与参数发现、通用模板验证、最后才做定向利用。
- **认证面**: 先收集默认配置、公开凭证线索与弱口令策略；仅在授权环境按节流与证据要求进行尝试。
- **未知/自定义协议**: 先做 banner/交互试探与协议确认，再决定使用何种探测/解析方式。

阶段与进度控制：
测试分为 4 个阶段：
1. **信息收集 (Reconnaissance)**: 完成后，请调用 `update_phase("Exploitation")`。
2. **漏洞利用 (Exploitation)**: 完成后，请调用 `update_phase("Persistence")`。
3. **权限维持 (Persistence)**: 完成后，请调用 `update_phase("Lateral Movement")`。
4. **内网横向 (Lateral Movement)**: 完成后，请生成最终报告并结束任务。

请用中文思考和回复。

以下是详细的 SOP 和工具使用指南，请严格遵守：
{tool_instructions}
"""

    def _write_report_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "write_report",
                "description": "将最终的调查结果报告写入磁盘。任务完成时请务必使用此工具。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "文件名 (例如 report_target.md)"
                        },
                        "content": {
                            "type": "string",
                            "description": "完整的Markdown格式报告内容，必须使用中文编写。"
                        }
                    },
                    "required": ["filename", "content"]
                }
            }
        }

    def _write_file_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "写入通用文件到磁盘 (例如 MSF 资源脚本 .rc)。不要用这个写最终报告。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "文件名 (例如 exploit.rc)"
                        },
                        "content": {
                            "type": "string",
                            "description": "文件内容"
                        }
                    },
                    "required": ["filename", "content"]
                }
            }
        }

    def _read_file_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取项目数据目录中的文本文件（用于分析报告、脚本与工具输出）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "文件路径（相对路径或绝对路径，必须位于项目目录内）",
                        },
                        "max_chars": {
                            "type": "integer",
                            "description": "最多读取字符数（默认 20000）",
                            "default": 20000,
                        },
                    },
                    "required": ["path"],
                },
            },
        }

    def _ipinfo_lookup_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "ipinfo_lookup",
                "description": "查询 IP/域名的基础画像（ASN、地理位置、组织等）。用于快速补全目标信息。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "IPv4 或域名"},
                    },
                    "required": ["query"],
                },
            },
        }

    def _shodan_internetdb_lookup_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "shodan_internetdb_lookup",
                "description": "通过 Shodan InternetDB（无需密钥）查询目标 IP 的开放端口/标签/CPE/已知 CVE 线索。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ip": {"type": "string", "description": "IPv4 地址"},
                    },
                    "required": ["ip"],
                },
            },
        }

    def _urlhaus_lookup_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "urlhaus_lookup",
                "description": "通过 URLhaus（无需密钥）查询恶意 URL/主机情报，用于钓鱼/恶意投递链路甄别。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string", "enum": ["host", "url"], "description": "查询类型"},
                        "indicator": {"type": "string", "description": "host 或 url"},
                    },
                    "required": ["kind", "indicator"],
                },
            },
        }

    def _search_knowledge_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "search_knowledge",
                "description": "搜索内部知识库和技能文档。支持语义搜索（例如 '如何利用 Log4j'）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词或自然语言问题 (例如 'SQL Injection', 'nmap', '提权')."
                        }
                    },
                    "required": ["query"]
                }
            }
        }

    def _save_playbook_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "save_playbook",
                "description": "保存可复用的漏洞验证/排障 Playbook（仅允许非破坏性验证与复现要点；不要写入可直接用于攻击的 EXP/POC 利用代码、shellcode 或持久化载荷）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "文件名（例如 'CVE-2021-44228_playbook.md'）"},
                        "content": {"type": "string", "description": "Markdown 内容（建议包含适用条件、验证步骤、证据采集、修复建议）"},
                    },
                    "required": ["filename", "content"],
                },
            },
        }

    def _search_playbooks_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "search_playbooks",
                "description": "在本地 Playbooks 中检索可复用的验证与排障方案（文件名/内容匹配）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "关键词或自然语言（如 CVE 编号/产品名/报错片段）"},
                        "limit": {"type": "integer", "default": 5, "description": "最大返回条目数"},
                    },
                    "required": ["query"],
                },
            },
        }

    def _search_exploit_db_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "search_exploit_db",
                "description": "搜索 Exploit-DB 漏洞库以查找可用的漏洞利用脚本 (Exploits)。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词 (例如 'Apache 2.4', 'CVE-2021-44228', 'WordPress Plugin')"
                        }
                    },
                    "required": ["query"]
                }
            }
        }

    def _update_phase_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "update_phase",
                "description": "更新当前渗透测试阶段。当你完成一个大阶段的工作（如信息收集）并准备进入下一个阶段时，必须调用此工具。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "next_phase": {
                            "type": "string",
                            "description": "下一个阶段名称",
                            "enum": ["Exploitation", "Persistence", "Lateral Movement", "Code Audit", "Reverse Engineering", "Report"]
                        }
                    },
                    "required": ["next_phase"]
                }
            }
        }

    def _web_search_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "联网搜索互联网（Bing/DDG 可选并自动回退）。当内部知识库没有相关信息时使用。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询词"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "最大结果数 (默认 5)",
                            "default": 5
                        },
                        "engine": {
                            "type": "string",
                            "description": "优先搜索引擎（默认 bing）",
                            "enum": ["bing", "ddg", "auto"],
                            "default": "bing",
                        },
                    },
                    "required": ["query"]
                }
            }
        }

    def _web_fetch_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "web_fetch",
                "description": "抓取指定网页并提取可读文本（仅允许 http/https 且禁止访问本地/内网地址）。用于把搜索到的资料页内容拉取进上下文，以便总结与沉淀。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "网页 URL（http/https）"},
                        "max_chars": {"type": "integer", "description": "最大返回字符数（默认 20000）", "default": 20000},
                    },
                    "required": ["url"],
                },
            },
        }

    def _add_knowledge_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "add_knowledge",
                "description": "将从互联网搜索到的新知识保存到本地知识库，以便未来使用。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "文件名 (例如 'CVE-2024-XXXX.md')"
                        },
                        "content": {
                            "type": "string",
                            "description": "Markdown 格式的知识内容"
                        },
                        "category": {
                            "type": "string",
                            "description": "分类目录 (例如 'Vulnerabilities', 'Tools', 'Exploits')",
                            "default": "General"
                        }
                    },
                    "required": ["filename", "content"]
                }
            }
        }

    def _register_vulnerability_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "register_vulnerability",
                "description": "登记已确认的漏洞发现（用于漏洞管理与报告跟踪）。仅登记已验证的漏洞与证据；不要写入可直接用于攻击的利用代码/持久化载荷。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "漏洞标题（简短清晰）"},
                        "severity": {"type": "string", "description": "风险等级：严重/高危/中危/低危", "enum": ["严重", "高危", "中危", "低危"]},
                        "cvss": {"type": "number", "description": "可选：CVSS v3.x 评分（0.0-10.0）"},
                        "affected": {"type": "string", "description": "受影响组件/URL/参数（例如 /login?user=... 或 SMB 服务）"},
                        "principle": {"type": "string", "description": "漏洞原理（高层解释，避免给出可直接复制的攻击载荷）"},
                        "evidence": {"type": "string", "description": "验证证据（日志摘要/响应片段/截图路径等，不要包含可直接执行的利用脚本）"},
                        "impact": {"type": "string", "description": "影响范围（数据泄露/命令执行/权限提升等）"},
                        "remediation": {"type": "string", "description": "修复建议（可操作）"},
                        "references": {"type": "string", "description": "参考链接/资料（可选）"},
                    },
                    "required": ["title", "severity", "principle", "evidence", "impact", "remediation"],
                },
            },
        }

    def _list_tools_catalog_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "list_tools_catalog",
                "description": "列出当前可用的外部工具目录（来自 config/tools/*.yaml），用于在不确定工具名或参数时查询。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "可选：按名称/描述过滤（子串匹配）"},
                        "limit": {"type": "integer", "description": "返回条数上限（默认 50）", "default": 50},
                    },
                    "required": [],
                },
            },
        }

    def _get_tool_info_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "get_tool_info",
                "description": "获取指定外部工具的参数定义与简要说明（来自 YAML）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "工具名（YAML 的 name）"},
                    },
                    "required": ["name"],
                },
            },
        }

    def _run_tool_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "run_tool",
                "description": "执行外部工具（来自 config/tools/*.yaml）。用于真实调用本地工具链并获取 stdout/stderr/return_code。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "工具名（YAML 的 name）"},
                        "args": {"type": "object", "description": "参数对象（键值对），键名需与 YAML parameters/args 对应"},
                    },
                    "required": ["name"],
                },
            },
        }

    def _get_openai_tools(self) -> List[Dict[str, Any]]:
        # Define internal tools
        internal_tools = [
            self._write_report_tool(), 
            self._write_file_tool(), 
            self._read_file_tool(),
            self._ipinfo_lookup_tool(),
            self._shodan_internetdb_lookup_tool(),
            self._urlhaus_lookup_tool(),
            self._search_knowledge_tool(), 
            self._search_exploit_db_tool(),
            self._update_phase_tool(),
            self._web_search_tool(),
            self._web_fetch_tool(),
            self._add_knowledge_tool(),
            self._save_playbook_tool(),
            self._search_playbooks_tool(),
            self._register_vulnerability_tool(),
            self._list_tools_catalog_tool(),
            self._get_tool_info_tool(),
            self._run_tool_tool(),
        ]

        return internal_tools

    def run(self, goal: str, stream_callback=None):
        raise NotImplementedError("请使用 run_stream() 进行 SSE 流式执行")

    def _sanitize_messages_for_deepseek(self):
        i = 0
        while i < len(self.messages):
            m = self.messages[i]
            if not isinstance(m, dict):
                i += 1
                continue

            if m.get("role") == "assistant":
                if "reasoning_content" not in m:
                    m["reasoning_content"] = ""

                tool_calls = m.get("tool_calls") or []
                if not tool_calls:
                    i += 1
                    continue

                pending_ids = []
                for tc in tool_calls:
                    if isinstance(tc, dict) and tc.get("id"):
                        pending_ids.append(tc["id"])

                if not pending_ids:
                    i += 1
                    continue

                responded = set()
                j = i + 1
                while j < len(self.messages):
                    nxt = self.messages[j]
                    if isinstance(nxt, dict) and nxt.get("role") == "assistant":
                        break
                    if isinstance(nxt, dict) and nxt.get("role") == "tool":
                        tcid = nxt.get("tool_call_id")
                        if tcid in pending_ids:
                            responded.add(tcid)
                    j += 1

                missing = [tcid for tcid in pending_ids if tcid not in responded]
                if missing:
                    insert_at = i + 1
                    while insert_at < len(self.messages):
                        nxt = self.messages[insert_at]
                        if not isinstance(nxt, dict):
                            break
                        if nxt.get("role") != "tool":
                            break
                        if nxt.get("tool_call_id") not in pending_ids:
                            break
                        insert_at += 1

                    for tcid in missing:
                        self.messages.insert(
                            insert_at,
                            {
                                "role": "tool",
                                "tool_call_id": tcid,
                                "content": "[系统补偿] 上一次工具调用缺少返回，已自动补齐。",
                            },
                        )
                        insert_at += 1
                        j += 1

                i = j
                continue

            i += 1

    def _looks_like_weaponized_payload(self, content: str) -> bool:
        s = (content or "").lower()
        if s.count("\\x") >= 8:
            return True
        markers = [
            "msfvenom",
            "meterpreter",
            "reverse_tcp",
            "reverse_http",
            "bind_tcp",
            "shellcode",
            "payload/",
            "use exploit/",
        ]
        return any(m in s for m in markers)

    def _summarize_pending_tool_calls(self) -> str:
        for idx in range(len(self.messages) - 1, -1, -1):
            m = self.messages[idx]
            if not isinstance(m, dict):
                continue
            if m.get("role") != "assistant":
                continue
            tool_calls = m.get("tool_calls") or []
            if not tool_calls:
                continue
            ids = []
            for tc in tool_calls:
                if isinstance(tc, dict) and tc.get("id"):
                    ids.append(tc["id"])
            if not ids:
                continue
            responded = set()
            for nxt in self.messages[idx + 1 :]:
                if not isinstance(nxt, dict):
                    break
                if nxt.get("role") == "assistant":
                    break
                if nxt.get("role") == "tool":
                    tcid = nxt.get("tool_call_id")
                    if tcid in ids:
                        responded.add(tcid)
            missing = [tcid for tcid in ids if tcid not in responded]
            return f"last_tool_calls={ids} responded={sorted(responded)} missing={missing}"
        return "no_pending_tool_calls"
    
    async def run_stream(self, goal: str):
        """Generator that yields SSE events"""
        # Reload API key from env (in case it changed via UI)
        if self.ai_provider == "openai":
            self.client.api_key = os.getenv("OPENAI_API_KEY", "sk-placeholder")
        else:
            self.client.api_key = os.getenv("DEEPSEEK_API_KEY", "sk-placeholder")

        try:
            tgt = ""
            for line in (goal or "").splitlines():
                if line.strip().startswith("目标IP:"):
                    tgt = line.split("目标IP:", 1)[-1].strip()
                    break
            self.target = tgt or ""
        except Exception:
            self.target = ""
        
        # MOE: Get initial system prompt based on phase
        current_expert = self.experts.get(self.current_phase, self.experts["Reconnaissance"])
        base_system_prompt = self.system_prompt # The big SOP
        expert_system_prompt = current_expert.get("system_prompt", "")
        
        # Combine prompts: Base SOP + Expert Focus
        full_system_prompt = f"{base_system_prompt}\n\n**当前专家角色**: {expert_system_prompt}"
        
        self.messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": f"{goal}"}
        ]
        
        # tools_schema will be dynamically fetched in loop if we want to change it per phase
        # But for now, fetch once at start. 
        # Wait, if phase changes, we need to refresh tools.
        # So we should move _get_openai_tools inside the loop or re-fetch on phase change.
        
        # Read max steps from config, default to 500
        try:
            max_steps = int(os.getenv("MAX_STEPS", "500"))
        except ValueError:
            max_steps = 500
            
        current_progress = 0
        
        yield {"type": "log", "content": f"[系统] 任务已启动: {goal}"}
        yield {"type": "log", "content": f"[MOE] 激活专家: {self.current_phase}"}
        
        try:
            for step in range(max_steps):
                try:
                    pe = getattr(self, "pause_event", None)
                    if pe is not None:
                        await pe.wait()
                except Exception:
                    pass

                # Refresh tools based on current phase (MOE)
                tools_schema = self._get_openai_tools()
                
                step_info = f"步骤 {step+1}/{max_steps}"
                logger.info(step_info)
                # yield {"type": "progress", "content": step+1, "total": max_steps} # Deprecated
                yield {"type": "log", "content": f"[系统] {step_info} - 思考中..."}
                
                try:
                    self._sanitize_messages_for_deepseek()
                    # DeepSeek Reasoner usually has reasoning_content
                    # We need to handle streaming from OpenAI client to get real-time thoughts
                    # But for now, let's keep it simple: non-streaming call, then output result
                    # Wrap blocking call in thread to avoid freezing asyncio loop
                    import asyncio
                    logger.info(f"LLM input check: {self._summarize_pending_tool_calls()}")
                    response = await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        messages=self.messages,
                        tools=tools_schema,
                        tool_choice="auto",
                        temperature=0.0
                    )
                except Exception as e:
                    err_text = str(e)
                    if "insufficient tool messages following tool_calls message" in err_text:
                        logger.warning(f"DeepSeek rejected messages (tool_calls/tool mismatch). Retrying after sanitize. {self._summarize_pending_tool_calls()}")
                        self._sanitize_messages_for_deepseek()
                        try:
                            response = await asyncio.to_thread(
                                self.client.chat.completions.create,
                                model=self.model,
                                messages=self.messages,
                                tools=tools_schema,
                                tool_choice="auto",
                                temperature=0.0
                            )
                        except Exception as e2:
                            yield {
                                "type": "error",
                                "content": f"调用 LLM 失败: {str(e2)} (provider={self.ai_provider}, model={self.model}, base_url={self.ai_base_url})",
                            }
                            return
                    else:
                        if "Error code: 401" in err_text or "authentication" in err_text.lower():
                            yield {
                                "type": "error",
                                "content": f"调用 LLM 失败(鉴权失败/401): 请检查 API Key 是否与当前厂家匹配且完整无空格 (provider={self.ai_provider}, model={self.model}, base_url={self.ai_base_url})",
                            }
                        else:
                            yield {
                                "type": "error",
                                "content": f"调用 LLM 失败: {err_text} (provider={self.ai_provider}, model={self.model}, base_url={self.ai_base_url})",
                            }
                        return
                
                msg = response.choices[0].message
                normalized_tool_calls = []
                if getattr(msg, "tool_calls", None):
                    for idx, tc in enumerate(msg.tool_calls):
                        tc_id = getattr(tc, "id", None) or f"tc_{step}_{idx}"
                        fn = tc.function
                        fn_args = fn.arguments
                        if not isinstance(fn_args, str):
                            fn_args = json.dumps(fn_args, ensure_ascii=False)
                        normalized_tool_calls.append(
                            {
                                "id": tc_id,
                                "type": "function",
                                "function": {"name": fn.name, "arguments": fn_args},
                            }
                        )

                reasoning_content = ""
                if hasattr(msg, "reasoning_content") and msg.reasoning_content:
                    reasoning_content = msg.reasoning_content
                assistant_msg = {
                    "role": "assistant",
                    "content": msg.content or "",
                    "reasoning_content": reasoning_content,
                }
                if normalized_tool_calls:
                    assistant_msg["tool_calls"] = normalized_tool_calls
                self.messages.append(assistant_msg)
                
                # If DeepSeek has reasoning content (Note: official OpenAI SDK might not parse 'reasoning_content' field yet standardly)
                # We can try to access extra fields if available, or just rely on content
                if reasoning_content:
                    yield {"type": "thought", "content": reasoning_content}
                
                if msg.content:
                    logger.info(f"Agent: {msg.content}")
                    yield {"type": "thought", "content": msg.content}
                
                if not normalized_tool_calls:
                    yield {"type": "log", "content": f"[系统] 任务结束: {msg.content}"}
                    yield {"type": "finish", "content": msg.content or ""}
                    # Ensure 100% on finish
                    yield {"type": "progress", "content": 100, "total": 100}
                    return
                
                deferred_messages = []
                for tool_call in normalized_tool_calls:
                    try:
                        pe = getattr(self, "pause_event", None)
                        if pe is not None:
                            await pe.wait()
                    except Exception:
                        pass
                    func_name = tool_call["function"]["name"]
                    try:
                        args_raw = tool_call["function"].get("arguments", "{}")
                        args = json.loads(args_raw) if isinstance(args_raw, str) else (args_raw or {})
                    except Exception:
                        args = {}

                    logger.info(f"Calling tool: {func_name} with {args}")
                    yield {"type": "log", "content": f"[工具调用] {func_name} 参数: {json.dumps(args, ensure_ascii=False)}"}

                    output = ""
                    try:
                        if func_name == "update_phase":
                            next_phase = args.get("next_phase")
                            phase_map = {
                                "Exploitation": 25,
                                "Persistence": 50,
                                "Lateral Movement": 75,
                                "Report": 90,
                            }
                            progress = phase_map.get(next_phase, current_progress)
                            if progress > current_progress:
                                current_progress = progress
                                yield {"type": "progress", "content": current_progress, "total": 100}
                                yield {"type": "log", "content": f"[阶段完成] 进入阶段: {next_phase} (进度 {current_progress}%)"}

                            output = f"阶段已更新为 {next_phase}"

                            if next_phase in self.experts:
                                self.current_phase = next_phase
                                new_expert = self.experts[next_phase]
                                deferred_messages.append(
                                    {"role": "system", "content": f"系统提示: 进入 {next_phase} 阶段。{new_expert['system_prompt']}"}
                                )
                                yield {"type": "log", "content": f"[MOE] 切换专家: {next_phase} Agent 已激活"}

                        elif func_name == "write_report":
                            report_dir = os.path.join(self.base_dir, "data", "reports")
                            os.makedirs(report_dir, exist_ok=True)
                            file_path = os.path.join(report_dir, args["filename"])
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(args["content"])
                            try:
                                from src.utils.report_renderer import render_report_html

                                base = os.path.splitext(args["filename"])[0]
                                html_name = base + ".html"
                                html_path = os.path.join(report_dir, html_name)
                                html = render_report_html(
                                    base_dir=self.base_dir,
                                    markdown_text=args["content"],
                                    filename=args["filename"],
                                    target=self.target,
                                )
                                with open(html_path, "w", encoding="utf-8") as hf:
                                    hf.write(html)
                                yield {"type": "log", "content": f"[成功] HTML 报告已生成: {html_name}"}
                            except Exception as e:
                                yield {"type": "log", "content": f"[警告] HTML 报告生成失败: {str(e)}"}
                            output = f"报告已成功写入 {file_path}"
                            yield {"type": "log", "content": f"[成功] 报告已生成: {args['filename']}"}

                        elif func_name == "register_vulnerability":
                            title = str(args.get("title", "")).strip()
                            severity = str(args.get("severity", "")).strip()
                            cvss = args.get("cvss", None)
                            affected = str(args.get("affected", "")).strip()
                            principle = str(args.get("principle", "")).strip()
                            evidence = str(args.get("evidence", "")).strip()
                            impact = str(args.get("impact", "")).strip()
                            remediation = str(args.get("remediation", "")).strip()
                            references = str(args.get("references", "")).strip()

                            if severity not in {"严重", "高危", "中危", "低危"}:
                                severity = "中危"
                            try:
                                cvss_val = float(cvss) if cvss is not None and str(cvss).strip() != "" else None
                            except Exception:
                                cvss_val = None

                            vuln = {
                                "task_id": self.task_id or "",
                                "target": getattr(self, "target", "") or "",
                                "title": title,
                                "severity": severity,
                                "cvss": cvss_val,
                                "status": "open",
                                "details": {
                                    "affected": affected,
                                    "principle": principle,
                                    "evidence": evidence,
                                    "impact": impact,
                                    "remediation": remediation,
                                    "references": references,
                                },
                            }

                            stored = vuln
                            if self.vuln_store is not None:
                                try:
                                    stored = self.vuln_store.upsert(vuln)
                                except Exception:
                                    stored = vuln

                            yield {"type": "vuln", "vuln": stored}
                            yield {"type": "log", "content": f"[漏洞] 已登记：{severity} - {title}"}
                            output = "漏洞已登记"

                        elif func_name == "write_file":
                            data_dir = os.path.join(self.base_dir, "data", "temp")
                            os.makedirs(data_dir, exist_ok=True)
                            file_path = os.path.join(data_dir, args["filename"])
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(args["content"])
                            output = f"文件已成功写入 {file_path}"
                            yield {"type": "log", "content": f"[文件] 已写入: {args['filename']}"}

                        elif func_name == "read_file":
                            req_path = args.get("path", "")
                            max_chars = args.get("max_chars", 20000)
                            try:
                                max_chars = int(max_chars)
                            except Exception:
                                max_chars = 20000
                            max_chars = max(100, min(max_chars, 200000))

                            candidate = req_path
                            if not os.path.isabs(candidate):
                                candidate = os.path.join(self.base_dir, candidate)
                            candidate = os.path.abspath(candidate)

                            base_abs = os.path.abspath(self.base_dir)
                            if not (candidate == base_abs or candidate.startswith(base_abs + os.sep)):
                                output = "拒绝访问：仅允许读取项目目录内的文件。"
                            elif not os.path.exists(candidate) or not os.path.isfile(candidate):
                                output = "文件不存在或不是普通文件。"
                            else:
                                with open(candidate, "r", encoding="utf-8", errors="replace") as f:
                                    content = f.read(max_chars + 1)
                                if len(content) > max_chars:
                                    content = content[:max_chars] + "\n...[内容已截断]..."
                                output = content

                        elif func_name == "ipinfo_lookup":
                            from src.utils.public_apis import ipinfo_lookup

                            query = args.get("query", "")
                            result = ipinfo_lookup(query)
                            output = json.dumps(result, ensure_ascii=False, indent=2)

                        elif func_name == "shodan_internetdb_lookup":
                            from src.utils.public_apis import shodan_internetdb_lookup

                            ip = args.get("ip", "")
                            result = shodan_internetdb_lookup(ip)
                            output = json.dumps(result, ensure_ascii=False, indent=2)

                        elif func_name == "urlhaus_lookup":
                            from src.utils.public_apis import urlhaus_lookup

                            kind = args.get("kind", "")
                            indicator = args.get("indicator", "")
                            result = urlhaus_lookup(kind, indicator)
                            output = json.dumps(result, ensure_ascii=False, indent=2)

                        elif func_name == "search_knowledge":
                            query = args.get("query", "")
                            use_fallback = False
                            base_dirs = [
                                os.path.join(self.base_dir, "data", "knowledge"),
                                os.path.join(self.base_dir, "data", "skills"),
                                os.path.join(self.base_dir, "data", "vulndb"),
                                os.path.join(self.base_dir, "data", "playbooks"),
                            ]
                            if not self.rag_engine._initialized:
                                yield {"type": "log", "content": "[知识库] 正在初始化向量数据库..."}
                                success = self.rag_engine.initialize()
                                if not success:
                                    use_fallback = True
                                else:
                                    if not self.rag_engine.collection or self.rag_engine.collection.count() == 0:
                                        yield {"type": "log", "content": "[知识库] 正在构建索引..."}
                                        for d in base_dirs:
                                            self.rag_engine.index_directory(d)

                            if use_fallback:
                                yield {"type": "log", "content": f"[知识库] RAG 不可用（依赖缺失或初始化失败），使用混合检索降级（关键词为主）: '{query}'"}
                                results = self.rag_engine.keyword_query(query, n_results=3, directories=base_dirs)
                            else:
                                yield {"type": "log", "content": f"[知识库] 正在混合检索（向量+关键词/RRF）: '{query}'"}
                                results = self.rag_engine.hybrid_query(
                                    query,
                                    n_results=3,
                                    directories=base_dirs,
                                    vector_n=8,
                                    lexical_n=12,
                                    rrf_k=60,
                                )

                            if not results:
                                output = "检索未返回结果。建议尝试更通用的关键词，或拆分为更短的关键短语重试。"
                                kg_results = []
                            else:
                                out_list = []
                                for r in results:
                                    meta = r.get("metadata", {})
                                    filename = meta.get("filename", "Unknown")
                                    source = meta.get("source", "")
                                    content = r.get("content", "")
                                    if source:
                                        try:
                                            source = os.path.relpath(source, self.base_dir)
                                        except Exception:
                                            pass
                                    extra = []
                                    if "rrf_score" in r:
                                        try:
                                            extra.append(f"rrf={float(r.get('rrf_score')):.4f}")
                                        except Exception:
                                            pass
                                    if "lexical_score" in r:
                                        try:
                                            extra.append(f"kw={float(r.get('lexical_score')):.3f}")
                                        except Exception:
                                            pass
                                    if "distance" in r and r.get("distance") is not None:
                                        try:
                                            extra.append(f"vec_dist={float(r.get('distance')):.4f}")
                                        except Exception:
                                            pass
                                    suffix = f" ({', '.join(extra)})" if extra else ""
                                    out_list.append(f"--- 来源: {source} (文件: {filename}){suffix} ---\n{content}\n")

                                kg_results = self.knowledge_graph.query_related(query, max_depth=1)
                                if kg_results:
                                    out_list.append("\n--- 知识图谱关联分析 ---")
                                    for kgr in kg_results:
                                        out_list.append(
                                            f"- 实体: {kgr['entity']} (关系: {kgr['relation']}, 类型: {kgr['type']})"
                                        )
                                output = "\n".join(out_list)

                            yield {
                                "type": "log",
                                "content": f"[知识库] 搜索完成，返回 {len(results)} 个文档 + {len(kg_results)} 个图谱关联",
                            }

                        elif func_name == "search_exploit_db":
                            query = args.get("query", "")
                            try:
                                stdout, stderr, code = await asyncio.to_thread(
                                    self.executor.execute, "searchsploit", {"query": query}, self.task_id
                                )
                                if code == 0:
                                    output = f"Exploit-DB 搜索结果:\n{stdout}"
                                    if not stdout.strip():
                                        output = (
                                            "未找到精确匹配的漏洞利用脚本。正在尝试更宽松的搜索条件..."
                                            "\n建议: 尝试移除具体的小版本号，只保留软件名称和主版本号重试 (例如 'OpenSSH 7.2' 而不是 'OpenSSH 7.2p2')。"
                                        )
                                else:
                                    output = f"搜索失败: {stderr or '未知错误'}"
                            except FileNotFoundError:
                                output = "错误: 系统中未找到 'searchsploit' 命令。请确保已安装 exploitdb。"

                            yield {"type": "log", "content": f"[漏洞库] 搜索 '{query}' 完成"}

                        elif func_name == "web_search":
                            query = args.get("query")
                            max_results = args.get("max_results", 5)
                            engine = args.get("engine", "bing")

                            yield {"type": "log", "content": f"[网络搜索] 正在搜索 ({engine}): {query}"}
                            results, meta = await asyncio.to_thread(
                                WebSearcher.search_with_meta, query, max_results, preferred_engine=engine
                            )
                            if not results:
                                attempts = meta.get("attempts") or []
                                err_lines = []
                                for a in attempts[:4]:
                                    eng = a.get("engine")
                                    ok = a.get("ok")
                                    e = a.get("error") or ""
                                    if ok:
                                        continue
                                    if e:
                                        err_lines.append(f"- {eng}: {e}")
                                    else:
                                        err_lines.append(f"- {eng}: failed")
                                hint = ""
                                if meta.get("proxy_set"):
                                    hint = "提示：已检测到代理配置；若仍失败，可能是搜索引擎反爬/网络限制，可尝试更换关键词或切换 engine。"
                                else:
                                    hint = "提示：未检测到代理配置；如处于受限网络环境，可配置 PROXY_URL 或系统 HTTP(S)_PROXY 后重试。"
                                details = "\n".join(err_lines).strip()
                                if details:
                                    output = f"网络搜索未返回结果，可能是网络/反爬/引擎不可用导致。\n{details}\n{hint}"
                                else:
                                    output = f"未找到相关结果。\n{hint}"
                            else:
                                formatted_results = []
                                for r in results:
                                    title = r.get("title", "No Title")
                                    body = r.get("body", "")
                                    href = r.get("href", "#")
                                    content_preview = f"- **{title}**\n  {body}\n  Link: {href}"
                                    formatted_results.append(content_preview)
                                output = "\n\n".join(formatted_results)

                            yield {"type": "log", "content": f"[网络搜索] 找到 {len(results)} 个结果"}

                        elif func_name == "web_fetch":
                            url = args.get("url", "")
                            max_chars = args.get("max_chars", 20000)
                            yield {"type": "log", "content": f"[网页抓取] 正在抓取: {url}"}
                            try:
                                data = await asyncio.to_thread(WebSearcher.fetch_url_text, url, max_chars)
                                title = data.get("title", "")
                                final_url = data.get("final_url", url)
                                truncated = bool(data.get("truncated"))
                                text = data.get("text", "")
                                output = f"Title: {title}\nURL: {final_url}\nTruncated: {truncated}\n\n{text}"
                            except Exception as e:
                                output = f"网页抓取失败: {str(e)}"
                            yield {"type": "log", "content": "[网页抓取] 完成"}

                        elif func_name == "add_knowledge":
                            filename = args.get("filename")
                            content = args.get("content")
                            category = args.get("category", "General")

                            category = "".join(x for x in category if x.isalnum() or x in " _-")
                            filename = "".join(x for x in filename if x.isalnum() or x in " ._-")
                            kb_dir = os.path.join(self.base_dir, "data", "knowledge")
                            if category and category != "General":
                                kb_dir = os.path.join(kb_dir, category)
                            os.makedirs(kb_dir, exist_ok=True)

                            file_path = os.path.join(kb_dir, filename)
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(content)
                            output = f"新知识已保存到 {category}/{filename}"
                            yield {"type": "log", "content": f"[知识库] {output}"}

                            if self.rag_engine._initialized:
                                yield {"type": "log", "content": "[知识库] 正在更新向量索引..."}
                                self.rag_engine.add_document(
                                    content=content,
                                    source=file_path,
                                    metadata={"filename": filename, "category": category},
                                )

                        elif func_name == "save_playbook":
                            filename = args.get("filename") or ""
                            content = args.get("content") or ""
                            filename = "".join(x for x in filename if x.isalnum() or x in " ._-")
                            if not filename.endswith(".md"):
                                filename += ".md"

                            if self._looks_like_weaponized_payload(content):
                                output = "拒绝保存：Playbook 仅允许非破坏性验证/排障内容，不允许保存可直接用于攻击的 EXP/POC 利用代码或 shellcode。"
                            else:
                                pb_dir = os.path.join(self.base_dir, "data", "playbooks")
                                os.makedirs(pb_dir, exist_ok=True)
                                file_path = os.path.join(pb_dir, filename)
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(content)
                                output = f"Playbook 已保存到 playbooks/{filename}"
                                yield {"type": "log", "content": f"[Playbook] {output}"}

                                if self.rag_engine._initialized:
                                    yield {"type": "log", "content": "[Playbook] 正在更新向量索引..."}
                                    self.rag_engine.add_document(
                                        content=content,
                                        source=file_path,
                                        metadata={"filename": filename, "type": "playbook"},
                                    )

                        elif func_name == "search_playbooks":
                            query = (args.get("query") or "").strip()
                            limit = args.get("limit", args.get("max_results", 5))
                            try:
                                limit = int(limit)
                            except Exception:
                                limit = 5
                            limit = max(1, min(limit, 20))

                            pb_dir = os.path.join(self.base_dir, "data", "playbooks")
                            if not os.path.exists(pb_dir):
                                output = "Playbooks 目录不存在。"
                            else:
                                terms = [t for t in re.split(r"\s+", query) if t]
                                scored = []
                                for fn in os.listdir(pb_dir):
                                    if not (fn.endswith(".md") or fn.endswith(".txt")):
                                        continue
                                    fp = os.path.join(pb_dir, fn)
                                    try:
                                        with open(fp, "r", encoding="utf-8", errors="replace") as f:
                                            text = f.read(200000)
                                    except Exception:
                                        continue
                                    hay = (fn + "\n" + text).lower()
                                    score = 0
                                    for t in terms:
                                        score += hay.count(t.lower())
                                    if score > 0:
                                        preview = ""
                                        for line in text.splitlines():
                                            if line.strip():
                                                preview = line.strip()
                                                break
                                        scored.append((score, fn, preview))

                                scored.sort(key=lambda x: (-x[0], x[1]))
                                top = scored[:limit]
                                if not top:
                                    output = "未找到匹配的 Playbook。"
                                else:
                                    out = []
                                    for score, fn, preview in top:
                                        out.append(f"- {fn} (score={score})\n  {preview}")
                                    output = "\n".join(out)

                        elif func_name == "list_tools_catalog":
                            query = (args.get("query") or "").strip().lower()
                            limit = args.get("limit", 50)
                            try:
                                limit = int(limit)
                            except Exception:
                                limit = 50
                            limit = max(1, min(limit, 200))

                            items = []
                            for td in self.tool_manager.list_tools():
                                if td.get("enabled", True) is False:
                                    continue
                                name = str(td.get("name") or "").strip()
                                if not name:
                                    continue
                                sd = (td.get("short_description") or td.get("description") or "").strip()
                                sd_line = ""
                                for line in sd.splitlines():
                                    if line.strip():
                                        sd_line = line.strip()
                                        break
                                hay = f"{name}\n{sd_line}".lower()
                                if query and query not in hay:
                                    continue

                                params = []
                                if isinstance(td.get("parameters"), list):
                                    for p in td["parameters"]:
                                        if not isinstance(p, dict):
                                            continue
                                        params.append(
                                            {
                                                "name": p.get("name"),
                                                "type": p.get("type", "string"),
                                                "required": bool(p.get("required", False)),
                                            }
                                        )
                                elif isinstance(td.get("args"), dict):
                                    for k, v in td["args"].items():
                                        if not isinstance(v, dict):
                                            v = {}
                                        params.append(
                                            {
                                                "name": k,
                                                "type": v.get("type", "string"),
                                                "required": bool(v.get("required", False)),
                                            }
                                        )

                                items.append(
                                    {
                                        "name": name,
                                        "short_description": sd_line,
                                        "parameters": params,
                                    }
                                )

                            output = json.dumps({"tools": items[:limit]}, ensure_ascii=False)
                            yield {"type": "log", "content": f"[工具目录] 返回 {min(len(items), limit)} 条"}

                        elif func_name == "get_tool_info":
                            name = str(args.get("name") or "").strip()
                            td = self.tool_manager.get_tool(name) if name else None
                            if not td or td.get("enabled", True) is False:
                                output = "未找到该工具或工具已禁用。"
                            else:
                                info = dict(td)
                                desc = (info.get("description") or "").strip()
                                if len(desc) > 4000:
                                    info["description"] = desc[:4000] + "\n...[已截断]..."
                                output = json.dumps(info, ensure_ascii=False)

                        elif func_name == "run_tool":
                            name = str(args.get("name") or "").strip()
                            tool_args = args.get("args", {})
                            if tool_args is None:
                                tool_args = {}
                            if isinstance(tool_args, str):
                                try:
                                    tool_args = json.loads(tool_args)
                                except Exception:
                                    tool_args = {}
                            if not isinstance(tool_args, dict):
                                output = "args 必须为对象（JSON）。"
                            else:
                                if name == "msfconsole" and (self.current_phase in {"Exploitation", "Persistence", "Lateral Movement"}):
                                    tool_args["keep_session"] = True
                                td = self.tool_manager.get_tool(name) if name else None
                                if not td or td.get("enabled", True) is False:
                                    output = "未找到该工具或工具已禁用。"
                                elif str(td.get("command") or "").strip().lower().startswith("internal:"):
                                    output = "该工具为占位/内部命令格式，当前运行时不支持直接执行。"
                                else:
                                    yield {"type": "log", "content": f"[执行中] {name}..."}
                                    stdout, stderr, code = await asyncio.to_thread(
                                        self.executor.execute, name, tool_args, self.task_id
                                    )
                                    output = f"标准输出:\n{stdout}\n错误输出:\n{stderr}\n返回码: {code}"
                                    display_out = stdout[:500] + "..." if len(stdout) > 500 else stdout
                                    if stderr:
                                        display_out += f"\n[Error] {stderr}"
                                    yield {"type": "log", "content": f"[工具结果] {name}:\n{display_out}"}
                                    if len(output) > 5000:
                                        output = output[:5000] + "\n...[输出已截断]..."

                        else:
                            yield {"type": "log", "content": f"[执行中] {func_name}..."}
                            if func_name == "msfconsole" and (self.current_phase in {"Exploitation", "Persistence", "Lateral Movement"}):
                                try:
                                    args["keep_session"] = True
                                except Exception:
                                    pass
                            stdout, stderr, code = await asyncio.to_thread(self.executor.execute, func_name, args, self.task_id)
                            output = f"标准输出:\n{stdout}\n错误输出:\n{stderr}\n返回码: {code}"
                            display_out = stdout[:500] + "..." if len(stdout) > 500 else stdout
                            if stderr:
                                display_out += f"\n[Error] {stderr}"
                            yield {"type": "log", "content": f"[工具结果] {func_name}:\n{display_out}"}
                            if len(output) > 5000:
                                output = output[:5000] + "\n...[输出已截断]..."

                    except Exception as e:
                        output = f"工具执行发生异常: {str(e)}"
                        yield {"type": "error", "content": output}

                    self.messages.append({"role": "tool", "tool_call_id": tool_call["id"], "content": str(output)})

                if deferred_messages:
                    self.messages.extend(deferred_messages)
            
            yield {"type": "error", "content": "达到最大步骤限制，未得出最终结论。"}
        
        except Exception as e:
            logger.error(f"Runtime error: {e}")
            yield {"type": "error", "content": f"运行时错误: {str(e)}"}
        finally:
            # Always finish at 100% on stop/error/finish
            yield {"type": "progress", "content": 100, "total": 100}
