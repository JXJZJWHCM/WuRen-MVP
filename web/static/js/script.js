document.addEventListener('DOMContentLoaded', () => {
    // === Variables ===
    let eventSource = null;
    
    // === DOM Elements ===
    const navItems = document.querySelectorAll('.nav-item');
    const pages = document.querySelectorAll('.page');
    
    const userInput = document.getElementById('userInput');
    const chatTaskSelect = document.getElementById('chatTaskSelect');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const chatMessages = document.getElementById('chat-messages');
    const healthBadge = document.getElementById('healthBadge');

    const perfMonitor = document.getElementById('perfMonitor');
    const perfCpu = document.getElementById('perfCpu');
    const perfMem = document.getElementById('perfMem');
    const perfDisk = document.getElementById('perfDisk');
    const perfDiskIo = document.getElementById('perfDiskIo');
    
    const reportList = document.getElementById('reportList');
    const refreshReportsBtn = document.getElementById('refreshReportsBtn');
    const reportModal = document.getElementById('reportModal');
    const closeModal = document.querySelector('.close-modal');

    const vulnList = document.getElementById('vulnList');
    const refreshVulnsBtn = document.getElementById('refreshVulnsBtn');
    const exportVulnsBtn = document.getElementById('exportVulnsBtn');
    const vulnTaskSelect = document.getElementById('vulnTaskSelect');
    const vulnSearchInput = document.getElementById('vulnSearchInput');
    const vulnSummaryBar = document.getElementById('vulnSummaryBar');
    const vulnSeverityFilter = document.getElementById('vulnSeverityFilter');
    const vulnStatusFilter = document.getElementById('vulnStatusFilter');
    const vulnModal = document.getElementById('vulnModal');
    const vulnModalTitle = document.getElementById('vulnModalTitle');
    const vulnModalBody = document.getElementById('vulnModalBody');
    const closeVulnModal = document.querySelector('.close-vuln-modal');

    const attackChainTaskSelect = document.getElementById('attackChainTaskSelect');
    const attackChainRefreshBtn = document.getElementById('attackChainRefreshBtn');
    const attackChainAutoRefresh = document.getElementById('attackChainAutoRefresh');
    const attackChainGraph = document.getElementById('attackChainGraph');
    const attackChainGraphSvg = document.getElementById('attackChainGraphSvg');
    const attackChainGraphEmpty = document.getElementById('attackChainGraphEmpty');
    const attackChainDetailMeta = document.getElementById('attackChainDetailMeta');
    const attackChainDetailStage = document.getElementById('attackChainDetailStage');
    const attackChainDetailType = document.getElementById('attackChainDetailType');
    const attackChainDetailDesc = document.getElementById('attackChainDetailDesc');
    const attackChainDetailTools = document.getElementById('attackChainDetailTools');
    const attackChainDetailRaw = document.getElementById('attackChainDetailRaw');

    const refreshProjectsBtn = document.getElementById('refreshProjectsBtn');
    const projectsAutoRefresh = document.getElementById('projectsAutoRefresh');
    const projectTargetInput = document.getElementById('projectTargetInput');
    const projectGoalInput = document.getElementById('projectGoalInput');
    const createProjectBtn = document.getElementById('createProjectBtn');
    const projectsList = document.getElementById('projectsList');
    const projectsDetailMeta = document.getElementById('projectsDetailMeta');
    const projectsDetailLog = document.getElementById('projectsDetailLog');
    const projectsStartBtn = document.getElementById('projectsStartBtn');
    const projectsPauseBtn = document.getElementById('projectsPauseBtn');
    const projectsResumeBtn = document.getElementById('projectsResumeBtn');
    const projectsStopBtn = document.getElementById('projectsStopBtn');
    const projectsDeleteBtn = document.getElementById('projectsDeleteBtn');

    const refreshAuditBtn = document.getElementById('refreshAuditBtn');
    const clearAuditBtn = document.getElementById('clearAuditBtn');
    const auditStatsText = document.getElementById('auditStatsText');
    const auditQueryInput = document.getElementById('auditQueryInput');
    const auditMethodSelect = document.getElementById('auditMethodSelect');
    const auditActionPreset = document.getElementById('auditActionPreset');
    const auditAdvancedKind = document.getElementById('auditAdvancedKind');
    const auditPathInput = document.getElementById('auditPathInput');
    const auditActionInput = document.getElementById('auditActionInput');
    const auditLogList = document.getElementById('auditLogList');
    const auditDetailMeta = document.getElementById('auditDetailMeta');
    const auditDetailRaw = document.getElementById('auditDetailRaw');
    const auditPrevBtn = document.getElementById('auditPrevBtn');
    const auditNextBtn = document.getElementById('auditNextBtn');
    const auditPageHint = document.getElementById('auditPageHint');

    const reconTaskSelect = document.getElementById('reconTaskSelect');
    const reconRefreshBtn = document.getElementById('reconRefreshBtn');
    const reconAutoRefresh = document.getElementById('reconAutoRefresh');
    const reconSummary = document.getElementById('reconSummary');
    const reconToolTags = document.getElementById('reconToolTags');
    const reconStepList = document.getElementById('reconStepList');
    const reconDetailMeta = document.getElementById('reconDetailMeta');
    const reconDetailTool = document.getElementById('reconDetailTool');
    const reconDetailCmd = document.getElementById('reconDetailCmd');
    const reconDetailRaw = document.getElementById('reconDetailRaw');

    const persistTaskSelect = document.getElementById('persistTaskSelect');
    const persistRefreshBtn = document.getElementById('persistRefreshBtn');
    const persistAutoRefresh = document.getElementById('persistAutoRefresh');
    const persistSummary = document.getElementById('persistSummary');
    const persistInfoBadge = document.getElementById('persistInfoBadge');
    const persistArtifactsBadge = document.getElementById('persistArtifactsBadge');
    const persistToolTags = document.getElementById('persistToolTags');
    const persistStepList = document.getElementById('persistStepList');
    const persistDetailMeta = document.getElementById('persistDetailMeta');
    const persistDetailTool = document.getElementById('persistDetailTool');
    const persistDetailCmd = document.getElementById('persistDetailCmd');
    const persistDetailArtifacts = document.getElementById('persistDetailArtifacts');
    const persistInfoBox = document.getElementById('persistInfoBox');
    const persistDetailRaw = document.getElementById('persistDetailRaw');

    const lateralTaskSelect = document.getElementById('lateralTaskSelect');
    const lateralRefreshBtn = document.getElementById('lateralRefreshBtn');
    const lateralAutoRefresh = document.getElementById('lateralAutoRefresh');
    const lateralSummary = document.getElementById('lateralSummary');
    const lateralPrivBadge = document.getElementById('lateralPrivBadge');
    const lateralCredBadge = document.getElementById('lateralCredBadge');
    const lateralHostBadge = document.getElementById('lateralHostBadge');
    const lateralArtifactsBadge = document.getElementById('lateralArtifactsBadge');
    const lateralToolTags = document.getElementById('lateralToolTags');
    const lateralStepList = document.getElementById('lateralStepList');
    const lateralDetailMeta = document.getElementById('lateralDetailMeta');
    const lateralDetailTool = document.getElementById('lateralDetailTool');
    const lateralDetailCmd = document.getElementById('lateralDetailCmd');
    const lateralDetailArtifacts = document.getElementById('lateralDetailArtifacts');
    const lateralInfoBox = document.getElementById('lateralInfoBox');
    const lateralDetailRaw = document.getElementById('lateralDetailRaw');

    const lootTaskSelect = document.getElementById('lootTaskSelect');
    const lootRefreshBtn = document.getElementById('lootRefreshBtn');
    const lootAutoRefresh = document.getElementById('lootAutoRefresh');
    const lootPathBar = document.getElementById('lootPathBar');
    const lootOverwriteToggle = document.getElementById('lootOverwriteToggle');
    const lootUploadInput = document.getElementById('lootUploadInput');
    const lootUpBtn = document.getElementById('lootUpBtn');
    const lootUploadBtn = document.getElementById('lootUploadBtn');
    const lootMkdirBtn = document.getElementById('lootMkdirBtn');
    const lootDownloadBtn = document.getElementById('lootDownloadBtn');
    const lootDeleteBtn = document.getElementById('lootDeleteBtn');
    const lootList = document.getElementById('lootList');
    const lootDetailMeta = document.getElementById('lootDetailMeta');
    const lootDetailPath = document.getElementById('lootDetailPath');
    const lootDetailSize = document.getElementById('lootDetailSize');
    const lootDetailMtime = document.getElementById('lootDetailMtime');
    const lootDetailPreview = document.getElementById('lootDetailPreview');
    const lootRemoteSessionSelect = document.getElementById('lootRemoteSessionSelect');
    const lootRemoteSessionInput = document.getElementById('lootRemoteSessionInput');
    const lootRemotePathInput = document.getElementById('lootRemotePathInput');
    const lootRemoteReadBtn = document.getElementById('lootRemoteReadBtn');
    const lootRemoteSaveBtn = document.getElementById('lootRemoteSaveBtn');
    const lootRemoteHint = document.getElementById('lootRemoteHint');

    const toolsList = document.getElementById('toolsList');
    const skillsList = document.getElementById('skillsList');
    const knowledgeList = document.getElementById('knowledgeList');
    const vulndbList = document.getElementById('vulndbList');
    
    const refreshSkillsBtn = document.getElementById('refreshSkillsBtn');
    const refreshKnowledgeBtn = document.getElementById('refreshKnowledgeBtn');

    const aiProviderSelect = document.getElementById('aiProviderSelect');
    const aiModelSelect = document.getElementById('aiModelSelect');
    const aiBaseUrlInput = document.getElementById('aiBaseUrlInput');
    const apiKeyLabel = document.getElementById('apiKeyLabel');
    const apiKeyHint = document.getElementById('apiKeyHint');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const ocrApiKeyInput = document.getElementById('ocrApiKeyInput');
    const ocrKeyModeSelect = document.getElementById('ocrKeyModeSelect');
    const ocrKeySection = document.getElementById('ocrKeySection');
    const ocrConfigHint = document.getElementById('ocrConfigHint');
    const ocrBaseUrlInput = document.getElementById('ocrBaseUrlInput');
    const ocrModelInput = document.getElementById('ocrModelInput');
    const ocrTimeoutInput = document.getElementById('ocrTimeoutInput');
    const maxStepsInput = document.getElementById('maxStepsInput');
    const auditLogMaxRowsInput = document.getElementById('auditLogMaxRowsInput');
    const proxyUrlInput = document.getElementById('proxyUrlInput');
    const bindInterfaceSelect = document.getElementById('bindInterfaceSelect');
    const lhostInput = document.getElementById('lhostInput');
    const bindInterfaceHint = document.getElementById('bindInterfaceHint');
    const effectiveLhostHint = document.getElementById('effectiveLhostHint');
    const languageSelect = document.getElementById('languageSelect');
    const toolWorkdirModeSelect = document.getElementById('toolWorkdirModeSelect');
    const toolMaxOutputCharsInput = document.getElementById('toolMaxOutputCharsInput');
    const toolSandboxSelect = document.getElementById('toolSandboxSelect');
    const toolDockerSection = document.getElementById('toolDockerSection');
    const toolDockerImageInput = document.getElementById('toolDockerImageInput');
    const toolDockerNetworkSelect = document.getElementById('toolDockerNetworkSelect');
    const toolDockerMemoryInput = document.getElementById('toolDockerMemoryInput');
    const toolDockerPidsLimitInput = document.getElementById('toolDockerPidsLimitInput');
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    const appVersionBadge = document.getElementById('appVersionBadge');
    const toolsCountBadge = document.getElementById('toolsCountBadge');
    const skillsCountBadge = document.getElementById('skillsCountBadge');
    const knowledgeCountBadge = document.getElementById('knowledgeCountBadge');
    const vulnDbTotalCountBadge = document.getElementById('vulnDbTotalCountBadge');
    
    let vulnState = {
        taskId: '',
        lastLoaded: [],
    };
    try {
        vulnState.taskId = (localStorage.getItem('vulnTaskId') || '').trim();
    } catch (e) {}

    let msfCliUiState = {
        taskId: '',
        vulnId: '',
        timer: null,
        seq: 0,
    };

    // === Initialization ===
    loadConfig();
    loadHealth();
    loadReports();
    loadTools();
    loadSkills();
    loadKnowledge();
    loadVulnerabilities();
    loadVulnDbStats();
    loadVulnManager();
    refreshProjectsData().catch(() => {});

    let attackChainState = {
        taskId: '',
        lastEventId: 0,
        events: [],
        timer: null,
        initialized: false,
        selectedStageId: '',
        taskMeta: null,
        stageEvidence: {},
        stageTools: {},
    };

    let projectsState = {
        selectedTaskId: '',
        tasks: [],
        lastEventId: 0,
        timer: null,
        initialized: false,
    };

    let auditState = {
        logs: [],
        selectedId: 0,
        offset: 0,
        limit: 200,
        initialized: false,
        timer: null,
    };

    let reconState = {
        taskId: '',
        taskMeta: null,
        events: [],
        lastEventId: 0,
        steps: [],
        tools: [],
        selectedStepId: 0,
        initialized: false,
        timer: null,
    };

    let persistState = {
        taskId: '',
        taskMeta: null,
        events: [],
        lastEventId: 0,
        steps: [],
        tools: [],
        artifacts: [],
        info: {},
        selectedStepId: 0,
        initialized: false,
        timer: null,
    };

    let lateralState = {
        taskId: '',
        taskMeta: null,
        events: [],
        lastEventId: 0,
        steps: [],
        tools: [],
        artifacts: [],
        info: {},
        selectedStepId: 0,
        initialized: false,
        timer: null,
    };

    let lootState = {
        taskId: '',
        path: '',
        entries: [],
        selectedPath: '',
        selectedEntry: null,
        remoteSessions: [],
        lastRemote: null,
        initialized: false,
        timer: null,
    };

    // === Add Content Logic ===
    const addModal = document.getElementById('addModal');
    const addModalTitle = document.getElementById('addModalTitle');
    const addFileName = document.getElementById('addFileName');
    const addFileContent = document.getElementById('addFileContent');
    const saveAddBtn = document.getElementById('saveAddBtn');
    const closeAddModal = document.querySelector('.close-add-modal');
    
    let currentAddType = ''; // 'tools', 'skills', 'knowledge'

    // Templates (Chinese)
    const templates = {
        skills: `# 技能名称

## 描述
简要描述该渗透测试技能或技术。

## 测试步骤/方法论
1. 第一步
2. 第二步

## 相关工具
- 工具 1
- 工具 2
`,
        knowledge: `# 知识条目标题

## 概览
这个漏洞或安全概念是什么？

## 影响
如果被利用，会产生什么后果？

## 缓解措施/修复建议
如何修复或预防此问题。
`,
        tools: `name: my_new_tool
description: 这是一个新工具的简短描述。
command: python my_script.py
args:
  target:
    description: 目标 IP 或 URL
    required: true
  port:
    description: 目标端口
    required: false
`
    };

    function openAddModal(type) {
        currentAddType = type;
        addModalTitle.textContent = `添加 ${type === 'tools' ? '工具' : type === 'skills' ? 'Skill' : '知识'}`;
        addFileName.value = '';
        addFileContent.value = templates[type] || '';
        addModal.style.display = 'block';
    }

    if (document.getElementById('addToolBtn')) {
        document.getElementById('addToolBtn').addEventListener('click', () => openAddModal('tools'));
    }
    if (document.getElementById('addSkillBtn')) {
        document.getElementById('addSkillBtn').addEventListener('click', () => openAddModal('skills'));
    }
    if (document.getElementById('addKnowledgeBtn')) {
        document.getElementById('addKnowledgeBtn').addEventListener('click', () => openAddModal('knowledge'));
    }

    if (closeAddModal) {
        closeAddModal.addEventListener('click', () => {
            addModal.style.display = 'none';
        });
    }

    if (saveAddBtn) {
        saveAddBtn.addEventListener('click', async () => {
            const filename = addFileName.value.trim();
            const content = addFileContent.value.trim();
            
            if (!filename || !content) {
                alert('请填写文件名和内容');
                return;
            }
            
            try {
                const res = await fetch(`/api/${currentAddType}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename, content })
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    alert('保存成功');
                    addModal.style.display = 'none';
                    // Refresh list
                    if (currentAddType === 'tools') loadTools();
                    else if (currentAddType === 'skills') loadSkills();
                    else if (currentAddType === 'knowledge') loadKnowledge();
                } else {
                    alert('保存失败: ' + (data.error || '未知错误'));
                }
            } catch (err) {
                console.error(err);
                alert('保存出错: ' + err.message);
            }
        });
    }

    // === Navigation ===
    function activatePage(targetId) {
        if (!targetId) return;
        const exists = Array.from(pages).some(p => p.id === targetId);
        if (!exists) return;

        navItems.forEach(nav => {
            nav.classList.toggle('active', nav.getAttribute('data-target') === targetId);
        });
        pages.forEach(page => {
            page.classList.toggle('active', page.id === targetId);
        });
        try {
            if (perfMonitor) {
                const page = document.getElementById(targetId);
                const center = page ? page.querySelector('.page-header .header-center') : null;
                if (center) center.appendChild(perfMonitor);
            }
        } catch (e) {}
        localStorage.setItem('activePage', targetId);
        try {
            if (location.hash !== `#${targetId}`) {
                history.replaceState(null, '', `#${targetId}`);
            }
        } catch (e) {}

        if (targetId === 'page-attackchain') {
            initAttackChainPage();
        }
        if (targetId === 'page-projects') {
            initProjectsPage();
        }
        if (targetId === 'page-auditlog') {
            initAuditLogPage();
        }
        if (targetId === 'page-recon') {
            initReconPage();
        }
        if (targetId === 'page-persistence') {
            initPersistencePage();
        }
        if (targetId === 'page-lateralmove') {
            initLateralMovePage();
        }
        if (targetId === 'page-loot') {
            initLootPage();
        }
    }

    const initialFromHash = (location.hash || '').replace('#', '').trim();
    const initialFromStorage = (localStorage.getItem('activePage') || '').trim();
    activatePage(initialFromHash || initialFromStorage || 'page-chat');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetId = item.getAttribute('data-target');
            activatePage(targetId);
            emitUiAudit('navigate', { page: targetId });
        });
    });

    function emitUiAudit(eventName, detail) {
        try {
            fetch('/api/audit/ui', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    event: String(eventName || ''),
                    detail: (detail && typeof detail === 'object') ? detail : {}
                }),
                keepalive: true
            }).catch(() => {});
        } catch (e) {}
    }

    function formatTs(tsSeconds) {
        try {
            const d = new Date((Number(tsSeconds) || 0) * 1000);
            return d.toLocaleString();
        } catch (e) {
            return '';
        }
    }

    function summarizeEventRow(row) {
        const ev = row && row.event ? row.event : {};
        const type = String(ev.type || '');
        const content = String(ev.content || '');
        if (type === 'log') {
            if (content.startsWith('[MOE]')) return { kind: 'phase', title: content, subtitle: '' };
            if (content.startsWith('[阶段完成]')) return { kind: 'phase', title: content, subtitle: '' };
            if (content.startsWith('[工具调用]')) {
                const m = content.match(/^\[工具调用\]\s+([^\s]+)\s+参数:\s+([\s\S]*)$/);
                const tool = m ? m[1] : 'tool';
                return { kind: 'tool', title: tool, subtitle: m ? m[2] : '' };
            }
            if (content.startsWith('[工具结果]')) {
                const m = content.match(/^\[工具结果\]\s+([^\s:]+)\s*:/);
                const tool = m ? m[1] : 'result';
                return { kind: 'result', title: tool, subtitle: '' };
            }
            return { kind: 'log', title: content, subtitle: '' };
        }
        if (type === 'thought') return { kind: 'thought', title: 'AI 输出', subtitle: content.slice(0, 160) };
        if (type === 'error') return { kind: 'error', title: '错误', subtitle: content.slice(0, 160) };
        if (type === 'finish') return { kind: 'finish', title: '任务结束', subtitle: content.slice(0, 160) };
        if (type === 'progress') return { kind: 'progress', title: '进度', subtitle: '' };
        return { kind: type || 'event', title: content.slice(0, 200), subtitle: '' };
    }

    function formatEventDetail(row) {
        const meta = row || {};
        const ev = meta.event || {};
        const lines = [];
        if (meta.id !== undefined) lines.push(`Event ID: ${meta.id}`);
        if (meta.ts) lines.push(`Time: ${formatTs(meta.ts)}`);
        if (ev.type) lines.push(`Type: ${ev.type}`);
        lines.push('');
        if (ev.content) {
            lines.push(String(ev.content));
        } else {
            try {
                lines.push(JSON.stringify(ev, null, 2));
            } catch (err) {
                lines.push(String(ev));
            }
        }
        return lines.join('\n');
    }

    const ATTACK_CHAIN_STAGES = [
        { id: 'recon', label: '信息收集', type: 'reconnaissance', desc: '识别资产、端口、服务与入口点', cls: 'attack-chain-stage-recon', pos: { left: '10%', top: '22%' } },
        { id: 'scan', label: '漏洞扫描', type: 'vulnerability_scanning', desc: '用自动化/半自动化手段发现潜在风险点', cls: 'attack-chain-stage-scan', pos: { left: '33%', top: '22%' } },
        { id: 'exploit', label: '漏洞利用', type: 'exploitation', desc: '在授权边界内验证漏洞可达与影响', cls: 'attack-chain-stage-exploit', pos: { left: '56%', top: '22%' } },
        { id: 'privesc', label: '权限提升', type: 'privilege_escalation', desc: '验证权限边界与配置风险（需授权）', cls: 'attack-chain-stage-privesc', pos: { left: '79%', top: '22%' } },
        { id: 'lateral', label: '横向移动', type: 'lateral_movement', desc: '评估内网扩散路径与信任关系（需授权）', cls: 'attack-chain-stage-lateral', pos: { left: '33%', top: '54%' } },
        { id: 'persist', label: '权限维持', type: 'persistence', desc: '后渗透风险评估与加固建议（不部署后门）', cls: 'attack-chain-stage-persist', pos: { left: '56%', top: '54%' } },
        { id: 'report', label: '报告生成', type: 'reporting', desc: '汇总证据、风险与修复建议并输出报告', cls: 'attack-chain-stage-report', pos: { left: '79%', top: '78%' } },
    ];

    const ATTACK_CHAIN_EDGES = [
        { from: 'recon', to: 'scan' },
        { from: 'scan', to: 'exploit' },
        { from: 'exploit', to: 'privesc' },
        { from: 'privesc', to: 'lateral' },
        { from: 'lateral', to: 'persist' },
        { from: 'persist', to: 'report' },
    ];

    function _toolFromLog(content) {
        const m = String(content || '').match(/^\[工具调用\]\s+([^\s]+)\s+参数:/);
        return m ? m[1] : '';
    }

    function _phaseFromLog(content) {
        const s = String(content || '');
        const m = s.match(/^\[MOE\]\s+(?:激活专家|切换专家):\s+([A-Za-z ]+)/);
        if (!m) return '';
        return String(m[1] || '').trim();
    }

    function _stageForTool(toolName) {
        const t = String(toolName || '').toLowerCase();
        const recon = new Set(['nmap', 'nmap-advanced', 'masscan', 'rustscan', 'amass', 'subfinder', 'gau', 'katana', 'hakrawler', 'dirsearch', 'gobuster', 'ffuf', 'feroxbuster', 'dnsenum', 'fierce', 'wafw00f', 'web_screenshot', 'nikto']);
        const scan = new Set(['nuclei', 'wpscan', 'sqlmap', 'dalfox', 'jaeles', 'wfuzz', 'xsser']);
        const exploit = new Set(['msfconsole', 'msfvenom', 'searchsploit']);
        const privesc = new Set(['linpeas', 'bloodhound', 'impacket', 'netexec', 'rpcclient', 'ssh', 'ncat']);
        const lateral = new Set(['responder', 'smbmap', 'arp-scan']);
        if (recon.has(t)) return 'recon';
        if (scan.has(t)) return 'scan';
        if (exploit.has(t)) return 'exploit';
        if (privesc.has(t)) return 'privesc';
        if (lateral.has(t)) return 'lateral';
        return '';
    }

    function _stageForPhase(phase) {
        const p = String(phase || '').toLowerCase();
        if (p === 'reconnaissance') return 'recon';
        if (p === 'exploitation') return 'scan';
        if (p === 'persistence') return 'privesc';
        if (p === 'lateral movement') return 'lateral';
        if (p === 'report') return 'report';
        return '';
    }

    function computeAttackChain(rows, taskMeta) {
        const evidence = {};
        const tools = {};
        ATTACK_CHAIN_STAGES.forEach(s => {
            evidence[s.id] = [];
            tools[s.id] = new Set();
        });

        let latestPhase = '';
        for (const r of rows || []) {
            const ev = r && r.event ? r.event : {};
            const type = String(ev.type || '');
            const content = String(ev.content || '');
            if (type === 'log') {
                const phase = _phaseFromLog(content);
                if (phase) latestPhase = phase;
                const tool = _toolFromLog(content);
                if (tool) {
                    const sid = _stageForTool(tool);
                    if (sid) {
                        evidence[sid].push(r);
                        tools[sid].add(tool);
                    }
                }
                if (content.includes('[成功] 报告已生成') || content.includes('报告已生成')) {
                    evidence.report.push(r);
                }
            } else if (type === 'report' || type === 'finish') {
                evidence.report.push(r);
            } else if (type === 'error') {
                const sid = _stageForPhase(latestPhase) || 'recon';
                evidence[sid].push(r);
            }
        }

        const activeStage = _stageForPhase(latestPhase);
        const metaStatus = taskMeta && taskMeta.status ? String(taskMeta.status).toLowerCase() : '';
        const stageStatus = {};
        ATTACK_CHAIN_STAGES.forEach((s, idx) => {
            const has = evidence[s.id] && evidence[s.id].length > 0;
            let st = has ? 'completed' : 'pending';
            if (activeStage && s.id === activeStage && metaStatus === 'running') st = 'active';
            if (activeStage && s.id === activeStage && metaStatus === 'paused') st = 'active';
            const hasErr = (evidence[s.id] || []).some(r => r && r.event && r.event.type === 'error');
            if (hasErr && (s.id === activeStage || metaStatus === 'error')) st = 'error';
            stageStatus[s.id] = st;
        });

        if (!attackChainState.selectedStageId) {
            const preferred = ATTACK_CHAIN_STAGES.find(s => stageStatus[s.id] === 'active')
                || [...ATTACK_CHAIN_STAGES].reverse().find(s => (evidence[s.id] || []).length)
                || ATTACK_CHAIN_STAGES[0];
            attackChainState.selectedStageId = preferred ? preferred.id : '';
        }

        return { evidence, tools, stageStatus, activeStage, metaStatus };
    }

    function buildAttackChainGraph() {
        if (!attackChainGraph || !attackChainGraphSvg) return;
        attackChainGraphSvg.innerHTML = '';
        const ns = 'http://www.w3.org/2000/svg';
        const defs = document.createElementNS(ns, 'defs');
        const marker = document.createElementNS(ns, 'marker');
        marker.setAttribute('id', 'acArrow');
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '10');
        marker.setAttribute('refX', '8');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');
        const path = document.createElementNS(ns, 'path');
        path.setAttribute('d', 'M0,0 L8,3 L0,6 Z');
        path.setAttribute('fill', 'rgba(120, 130, 140, 0.95)');
        marker.appendChild(path);
        defs.appendChild(marker);
        attackChainGraphSvg.appendChild(defs);

        ATTACK_CHAIN_STAGES.forEach(s => {
            let el = attackChainGraph.querySelector(`[data-stage="${s.id}"]`);
            if (!el) {
                el = document.createElement('div');
                el.className = `attack-chain-stage ${s.cls} is-pending`;
                el.dataset.stage = s.id;
                el.style.left = s.pos.left;
                el.style.top = s.pos.top;
                el.textContent = s.label;
                el.addEventListener('click', () => {
                    attackChainState.selectedStageId = s.id;
                    if (attackChainState.taskId) {
                        emitUiAudit('attackchain_select_stage', { task_id: attackChainState.taskId, stage_id: s.id });
                    }
                    renderAttackChain();
                });
                el.addEventListener('mouseenter', () => {
                    attackChainState.selectedStageId = s.id;
                    renderAttackChain();
                });
                attackChainGraph.appendChild(el);
            }
        });
    }

    function drawAttackChainEdges() {
        if (!attackChainGraph || !attackChainGraphSvg) return;
        const ns = 'http://www.w3.org/2000/svg';
        const rect = attackChainGraph.getBoundingClientRect();
        const w = rect.width || 1;
        const h = rect.height || 1;
        attackChainGraphSvg.setAttribute('viewBox', `0 0 ${w} ${h}`);
        const existing = Array.from(attackChainGraphSvg.querySelectorAll('line, path')).filter(n => n.tagName !== 'defs');
        existing.forEach(n => n.remove());

        function centerOf(stageId) {
            const el = attackChainGraph.querySelector(`[data-stage="${stageId}"]`);
            if (!el) return { x: 0, y: 0 };
            const r = el.getBoundingClientRect();
            return { x: (r.left - rect.left) + r.width / 2, y: (r.top - rect.top) + r.height / 2 };
        }

        ATTACK_CHAIN_EDGES.forEach(e => {
            const a = centerOf(e.from);
            const b = centerOf(e.to);
            const line = document.createElementNS(ns, 'line');
            line.setAttribute('x1', String(a.x));
            line.setAttribute('y1', String(a.y));
            line.setAttribute('x2', String(b.x));
            line.setAttribute('y2', String(b.y));
            line.setAttribute('stroke', 'rgba(120, 130, 140, 0.7)');
            line.setAttribute('stroke-width', '3');
            line.setAttribute('stroke-dasharray', '8 8');
            line.setAttribute('marker-end', 'url(#acArrow)');
            attackChainGraphSvg.appendChild(line);
        });
    }

    function renderAttackChainDetail(stageId, computed) {
        const stage = ATTACK_CHAIN_STAGES.find(s => s.id === stageId) || ATTACK_CHAIN_STAGES[0];
        const evs = (computed.evidence[stage.id] || []);
        const toolSet = computed.tools[stage.id] || new Set();
        const st = computed.stageStatus[stage.id] || 'pending';

        if (attackChainDetailMeta) {
            const t = attackChainState.taskId ? `任务：${attackChainState.taskId}` : '任务：—';
            const meta = [];
            if (attackChainState.taskMeta && attackChainState.taskMeta.status) meta.push(`状态：${attackChainState.taskMeta.status}`);
            if (evs.length) meta.push(`节点：${evs.length}`);
            const lastTs = evs.length ? (evs[evs.length - 1].ts || 0) : 0;
            if (lastTs) meta.push(`最新：${formatTs(lastTs)}`);
            attackChainDetailMeta.textContent = `${t}` + (meta.length ? `  ·  ${meta.join('  ·  ')}` : '');
        }
        if (attackChainDetailStage) attackChainDetailStage.textContent = stage.label;
        if (attackChainDetailType) attackChainDetailType.textContent = stage.type;
        if (attackChainDetailDesc) attackChainDetailDesc.textContent = stage.desc;

        if (attackChainDetailTools) {
            attackChainDetailTools.innerHTML = '';
            const toolsSorted = Array.from(toolSet).map(x => String(x)).filter(Boolean).sort((a, b) => a.localeCompare(b));
            if (!toolsSorted.length) {
                const tag = document.createElement('div');
                tag.className = 'attack-chain-tool-tag';
                tag.textContent = '—';
                attackChainDetailTools.appendChild(tag);
            } else {
                toolsSorted.slice(0, 24).forEach(tn => {
                    const tag = document.createElement('div');
                    tag.className = 'attack-chain-tool-tag';
                    tag.textContent = tn;
                    attackChainDetailTools.appendChild(tag);
                });
            }
        }

        if (attackChainDetailRaw) {
            const latest = evs.length ? evs[evs.length - 1] : null;
            if (!latest) {
                attackChainDetailRaw.textContent = '将鼠标移动到流程节点以查看详情。';
            } else {
                attackChainDetailRaw.textContent = formatEventDetail(latest);
            }
        }
    }

    function renderAttackChain() {
        if (!attackChainGraph || !attackChainGraphSvg) return;
        const hasTask = Boolean(attackChainState.taskId);
        if (attackChainGraphEmpty) attackChainGraphEmpty.style.display = hasTask ? 'none' : 'flex';
        if (!hasTask) {
            if (attackChainDetailMeta) attackChainDetailMeta.textContent = '—';
            if (attackChainDetailStage) attackChainDetailStage.textContent = '—';
            if (attackChainDetailType) attackChainDetailType.textContent = '—';
            if (attackChainDetailDesc) attackChainDetailDesc.textContent = '—';
            if (attackChainDetailTools) attackChainDetailTools.innerHTML = '';
            if (attackChainDetailRaw) attackChainDetailRaw.textContent = '将鼠标移动到流程节点以查看详情。';
            return;
        }

        buildAttackChainGraph();
        const computed = computeAttackChain(attackChainState.events || [], attackChainState.taskMeta || null);
        attackChainState.stageEvidence = computed.evidence;
        attackChainState.stageTools = computed.tools;

        ATTACK_CHAIN_STAGES.forEach(s => {
            const el = attackChainGraph.querySelector(`[data-stage="${s.id}"]`);
            if (!el) return;
            el.classList.remove('is-active', 'is-completed', 'is-pending', 'is-error');
            const st = computed.stageStatus[s.id] || 'pending';
            el.classList.add(`is-${st}`);
            if (attackChainState.selectedStageId === s.id) el.classList.add('is-active');
        });

        drawAttackChainEdges();
        renderAttackChainDetail(attackChainState.selectedStageId, computed);
    }

    async function loadAttackChainTasks() {
        if (!attackChainTaskSelect) return;
        try {
            const res = await fetch('/api/tasks?limit=200');
            const data = await res.json();
            const tasks = Array.isArray(data.tasks) ? data.tasks : [];
            const current = attackChainTaskSelect.value;
            attackChainTaskSelect.innerHTML = '<option value=\"\">选择项目/任务...</option>';
            for (const t of tasks) {
                if (!t || !t.task_id) continue;
                const opt = document.createElement('option');
                opt.value = String(t.task_id);
                const goal = String(t.goal || '').replace(/\s+/g, ' ').trim();
                const goalShort = goal.length > 60 ? (goal.slice(0, 60) + '…') : goal;
                const status = String(t.status || '');
                opt.textContent = `${t.task_id}  ·  ${status}` + (goalShort ? `  ·  ${goalShort}` : '');
                attackChainTaskSelect.appendChild(opt);
            }
            if (current) attackChainTaskSelect.value = current;
        } catch (e) {}
    }

    async function loadAttackChainEvents(taskId, reset = false) {
        if (!taskId) return;
        const limit = 5000;
        const sinceId = reset ? 0 : (attackChainState.lastEventId || 0);
        try {
            try {
                const metaRes = await fetch(`/api/tasks/${encodeURIComponent(taskId)}`);
                const meta = await metaRes.json().catch(() => null);
                if (metaRes.ok && meta && meta.task_id) {
                    attackChainState.taskMeta = meta;
                }
            } catch (e) {}
            const res = await fetch(`/api/tasks/${encodeURIComponent(taskId)}/events?limit=${limit}&since_id=${encodeURIComponent(String(sinceId))}`);
            const data = await res.json();
            const rows = Array.isArray(data.events) ? data.events : [];
            if (reset) {
                attackChainState.events = rows;
            } else if (rows.length) {
                attackChainState.events = (attackChainState.events || []).concat(rows);
            }
            if (attackChainState.events && attackChainState.events.length) {
                const last = attackChainState.events[attackChainState.events.length - 1];
                if (last && last.id) attackChainState.lastEventId = last.id;
            }
            renderAttackChain();
        } catch (e) {}
    }

    function stopAttackChainTimer() {
        if (attackChainState.timer) {
            clearInterval(attackChainState.timer);
            attackChainState.timer = null;
        }
    }

    function startAttackChainTimer() {
        stopAttackChainTimer();
        attackChainState.timer = setInterval(() => {
            if (!attackChainState.taskId) return;
            if (!attackChainAutoRefresh || !attackChainAutoRefresh.checked) return;
            loadAttackChainEvents(attackChainState.taskId, false);
        }, 1500);
    }

    function initAttackChainPage() {
        if (attackChainState.initialized) {
            startAttackChainTimer();
            try {
                drawAttackChainEdges();
            } catch (e) {}
            return;
        }
        attackChainState.initialized = true;
        loadAttackChainTasks().then(() => {});
        renderAttackChain();

        if (attackChainTaskSelect) {
            attackChainTaskSelect.addEventListener('change', async () => {
                const taskId = String(attackChainTaskSelect.value || '').trim();
                attackChainState.taskId = taskId;
                attackChainState.lastEventId = 0;
                attackChainState.events = [];
                renderAttackChain();
                if (taskId) {
                    emitUiAudit('attackchain_select_task', { task_id: taskId });
                    await loadAttackChainEvents(taskId, true);
                }
            });
        }
        if (attackChainRefreshBtn) {
            attackChainRefreshBtn.addEventListener('click', async () => {
                await loadAttackChainTasks();
                if (attackChainState.taskId) {
                    await loadAttackChainEvents(attackChainState.taskId, true);
                }
            });
        }
        if (attackChainAutoRefresh) {
            attackChainAutoRefresh.addEventListener('change', () => {
                startAttackChainTimer();
            });
        }
        startAttackChainTimer();
        try {
            window.addEventListener('resize', () => {
                if (!attackChainState.taskId) return;
                drawAttackChainEdges();
            });
        } catch (e) {}
    }

    function statusLabel(status) {
        const s = String(status || '').toLowerCase();
        if (s === 'running') return { text: '运行中', cls: 'status-success' };
        if (s === 'paused') return { text: '已暂停', cls: 'status-warning' };
        if (s === 'created') return { text: '未开始', cls: 'status-warning' };
        if (s === 'cancelled') return { text: '已停止', cls: 'status-danger' };
        if (s === 'error') return { text: '异常', cls: 'status-danger' };
        if (s === 'finished') return { text: '已完成', cls: 'status-success' };
        return { text: status || 'unknown', cls: 'status-warning' };
    }

    async function fetchTasks(limit = 200) {
        const res = await fetch(`/api/tasks?limit=${encodeURIComponent(String(limit))}`);
        const data = await res.json();
        return Array.isArray(data.tasks) ? data.tasks : [];
    }

    function syncChatTaskSelect(tasks) {
        if (!chatTaskSelect) return;
        const current = String(chatTaskSelect.value || '');
        chatTaskSelect.innerHTML = '<option value=\"\">选择项目/任务...</option>';
        (tasks || []).forEach(t => {
            if (!t || !t.task_id) return;
            const opt = document.createElement('option');
            opt.value = String(t.task_id);
            const st = statusLabel(t.status);
            opt.textContent = `${t.task_id}  ·  ${st.text}`;
            chatTaskSelect.appendChild(opt);
        });
        if (current) chatTaskSelect.value = current;
    }

    async function ensureTaskStarted(taskId, goal = '') {
        const r = await fetch(`/api/tasks/${encodeURIComponent(taskId)}/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal: goal || '' }),
        });
        const data = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(data.error || 'start_failed');
        return data;
    }

    async function loadTaskMeta(taskId) {
        const r = await fetch(`/api/tasks/${encodeURIComponent(taskId)}`);
        const data = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(data.error || 'task_not_found');
        return data;
    }

    async function loadTaskEvents(taskId, sinceId = 0, limit = 5000) {
        const r = await fetch(`/api/tasks/${encodeURIComponent(taskId)}/events?limit=${encodeURIComponent(String(limit))}&since_id=${encodeURIComponent(String(sinceId || 0))}`);
        const data = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(data.error || 'events_failed');
        return Array.isArray(data.events) ? data.events : [];
    }

    async function startChatForTask(taskId, goal = '', isRecovery = false) {
        const target = String(taskId || '').trim();
        if (!target) return;

        emitUiAudit('task_start', { task_id: target, source: isRecovery ? 'recovery' : 'chat', has_goal: Boolean((goal || '').trim()) });

        const welcomeScreen = chatMessages.querySelector('.welcome-screen');
        if (welcomeScreen) welcomeScreen.remove();

        chatMessages.innerHTML = '';
        appendMessage('user', target);

        if (chatTaskSelect) chatTaskSelect.value = target;
        localStorage.setItem('currentTask', JSON.stringify({ target: target, timestamp: Date.now() }));

        userInput.value = '';
        userInput.disabled = true;
        userInput.placeholder = isRecovery ? `正在扫描: ${target} (任务恢复中...)` : `正在扫描: ${target} (任务进行中...)`;

        startBtn.disabled = true;
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-flex';
        stopBtn.disabled = false;

        try {
            const startInfo = await ensureTaskStarted(target, goal);
            connectSSE(startInfo.stream_url || `/api/scan/stream?target=${encodeURIComponent(target)}`);
        } catch (e) {
            localStorage.removeItem('currentTask');
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            startBtn.disabled = false;
            startBtn.style.display = 'inline-flex';
            stopBtn.style.display = 'none';
            userInput.disabled = false;
            userInput.placeholder = '输入目标 IP 或域名 (例如: 192.168.1.1)';
            appendMessage('error', `启动失败: ${e.message || e}`);
            return;
        }
        try {
            await refreshProjectsData();
        } catch (e) {}
    }

    async function showTaskInChat(taskId) {
        const target = String(taskId || '').trim();
        if (!target) return;

        emitUiAudit('chat_select_task', { task_id: target });

        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }

        const welcomeScreen = chatMessages.querySelector('.welcome-screen');
        if (welcomeScreen) welcomeScreen.remove();
        chatMessages.innerHTML = '';
        appendMessage('user', target);

        const meta = await loadTaskMeta(target);
        const events = await loadTaskEvents(target, 0, 8000);
        for (const row of events) {
            if (!row || !row.event) continue;
            if (row.event.type === 'log') continue;
            handleStreamEvent(row.event);
        }

        if (meta.status === 'running' || meta.status === 'paused') {
            localStorage.setItem('currentTask', JSON.stringify({ target: target, timestamp: Date.now() }));
            userInput.value = '';
            userInput.disabled = true;
            userInput.placeholder = meta.status === 'paused' ? `任务已暂停: ${target}` : `正在扫描: ${target} (任务进行中...)`;
            startBtn.disabled = true;
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-flex';
            stopBtn.disabled = false;
            connectSSE(`/api/scan/stream?target=${encodeURIComponent(target)}&goal=`);
        } else {
            userInput.disabled = false;
            userInput.placeholder = '输入目标 IP 或域名 (例如: 192.168.1.1)';
            startBtn.disabled = false;
            startBtn.style.display = 'inline-flex';
            stopBtn.style.display = 'none';
        }
    }

    async function refreshProjectsData() {
        const tasks = await fetchTasks(200);
        projectsState.tasks = tasks;
        syncChatTaskSelect(tasks);
        syncVulnTaskSelect(tasks);
        if (projectsState.initialized) {
            renderProjectsList(tasks);
            if (projectsState.selectedTaskId) {
                await loadProjectsLog(projectsState.selectedTaskId, false);
                await updateProjectsDetailMeta(projectsState.selectedTaskId);
            }
        }
        if (attackChainState.initialized) {
            await loadAttackChainTasks();
        }
        if (reconState.initialized) {
            await loadReconTasks();
        }
        if (persistState.initialized) {
            await loadPersistenceTasks();
        }
        if (lateralState.initialized) {
            await loadLateralTasks();
        }
        if (lootState.initialized) {
            await loadLootTasks();
        }
    }

    function syncVulnTaskSelect(tasks) {
        if (!vulnTaskSelect) return;
        const stored = (localStorage.getItem('vulnTaskId') || '').trim();
        const current = String(vulnTaskSelect.value || vulnState.taskId || stored || '');
        vulnTaskSelect.innerHTML = '<option value=\"\">请选择项目/任务...</option>';
        (tasks || []).forEach(t => {
            if (!t || !t.task_id) return;
            const opt = document.createElement('option');
            opt.value = String(t.task_id);
            const st = statusLabel(t.status);
            opt.textContent = `${t.task_id}  ·  ${st.text}`;
            vulnTaskSelect.appendChild(opt);
        });
        if (current) {
            vulnTaskSelect.value = current;
            vulnState.taskId = current;
        } else if (projectsState && projectsState.selectedTaskId) {
            vulnTaskSelect.value = projectsState.selectedTaskId;
            vulnState.taskId = projectsState.selectedTaskId;
        }
    }

    function renderProjectsList(tasks) {
        if (!projectsList) return;
        projectsList.innerHTML = '';
        const frag = document.createDocumentFragment();
        (tasks || []).forEach(t => {
            if (!t || !t.task_id) return;
            const id = String(t.task_id);
            const st = statusLabel(t.status);
            const item = document.createElement('div');
            item.className = 'project-item' + (projectsState.selectedTaskId === id ? ' active' : '');
            item.dataset.taskId = id;

            const left = document.createElement('div');
            left.className = 'project-item-left';
            const title = document.createElement('div');
            title.className = 'project-item-title';
            title.textContent = id;
            const meta = document.createElement('div');
            meta.className = 'project-item-meta';
            const goal = String(t.goal || '').replace(/\s+/g, ' ').trim();
            meta.textContent = goal.length > 80 ? (goal.slice(0, 80) + '…') : goal;
            left.appendChild(title);
            left.appendChild(meta);

            const right = document.createElement('div');
            right.className = 'project-item-right';
            const badge = document.createElement('span');
            badge.className = `status-badge ${st.cls}`;
            badge.textContent = st.text;
            right.appendChild(badge);

            item.appendChild(left);
            item.appendChild(right);
            item.addEventListener('click', async () => {
                projectsState.selectedTaskId = id;
                projectsState.lastEventId = 0;
                if (projectsDetailLog) projectsDetailLog.textContent = '';
                renderProjectsList(projectsState.tasks);
                await updateProjectsDetailMeta(id);
                await loadProjectsLog(id, true);
            });
            frag.appendChild(item);
        });
        projectsList.appendChild(frag);
    }

    async function updateProjectsDetailMeta(taskId) {
        if (!projectsDetailMeta) return;
        try {
            const meta = await loadTaskMeta(taskId);
            const st = statusLabel(meta.status);
            const updated = meta.updated_at ? formatTs(meta.updated_at) : '';
            projectsDetailMeta.textContent = `任务：${taskId}  ·  状态：${st.text}` + (updated ? `  ·  更新：${updated}` : '');
        } catch (e) {
            projectsDetailMeta.textContent = `任务：${taskId}`;
        }
    }

    function appendProjectsLogLine(line) {
        if (!projectsDetailLog) return;
        projectsDetailLog.textContent += line + '\n';
        projectsDetailLog.scrollTop = projectsDetailLog.scrollHeight;
    }

    async function loadProjectsLog(taskId, reset = false) {
        if (!taskId) return;
        const sinceId = reset ? 0 : (projectsState.lastEventId || 0);
        const rows = await loadTaskEvents(taskId, sinceId, 5000);
        if (reset && projectsDetailLog) projectsDetailLog.textContent = '';
        for (const row of rows) {
            const ev = row.event || {};
            const ts = row.ts ? formatTs(row.ts) : '';
            const head = ts ? `[${ts}] ` : '';
            const text = (ev && ev.content) ? String(ev.content) : JSON.stringify(ev);
            appendProjectsLogLine(`${head}${ev.type || 'event'}: ${text}`);
            projectsState.lastEventId = row.id || projectsState.lastEventId;
        }
    }

    function stopProjectsTimer() {
        if (projectsState.timer) {
            clearInterval(projectsState.timer);
            projectsState.timer = null;
        }
    }

    function startProjectsTimer() {
        stopProjectsTimer();
        projectsState.timer = setInterval(async () => {
            try {
                if (projectsAutoRefresh && !projectsAutoRefresh.checked) return;
                await refreshProjectsData();
            } catch (e) {}
        }, 1500);
    }

    function initProjectsPage() {
        if (projectsState.initialized) {
            startProjectsTimer();
            return;
        }
        projectsState.initialized = true;

        if (projectsDetailLog) projectsDetailLog.textContent = '';
        if (projectsDetailMeta) projectsDetailMeta.textContent = '请选择一个任务以查看日志。';

        refreshProjectsData().then(() => {});
        startProjectsTimer();

        if (refreshProjectsBtn) {
            refreshProjectsBtn.addEventListener('click', async () => {
                await refreshProjectsData();
            });
        }
        if (projectsAutoRefresh) {
            projectsAutoRefresh.addEventListener('change', () => {
                startProjectsTimer();
            });
        }
        if (createProjectBtn) {
            createProjectBtn.addEventListener('click', async () => {
                const taskId = String(projectTargetInput ? projectTargetInput.value : '').trim();
                if (!taskId) {
                    alert('请输入目标/项目名称');
                    return;
                }
                const goal = String(projectGoalInput ? projectGoalInput.value : '').trim();
                emitUiAudit('task_create', { task_id: taskId, has_goal: Boolean(goal) });
                const r = await fetch('/api/tasks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task_id: taskId, goal }),
                });
                const data = await r.json().catch(() => ({}));
                if (!r.ok) {
                    alert(data.error || '创建失败');
                    return;
                }
                if (projectTargetInput) projectTargetInput.value = '';
                await refreshProjectsData();
                projectsState.selectedTaskId = taskId;
                projectsState.lastEventId = 0;
                renderProjectsList(projectsState.tasks);
                await updateProjectsDetailMeta(taskId);
                await loadProjectsLog(taskId, true);
            });
        }

        async function actionOnSelected(action) {
            const taskId = String(projectsState.selectedTaskId || '').trim();
            if (!taskId) {
                alert('请先在左侧任务列表中选择一个任务。');
                return;
            }
            if (action === 'start') {
                const goal = String(projectGoalInput ? projectGoalInput.value : '').trim();
                emitUiAudit('task_start', { task_id: taskId, source: 'projects', has_goal: Boolean(goal) });
                activatePage('page-chat');
                await startChatForTask(taskId, goal, false);
                return;
            }
            if (action === 'pause') {
                emitUiAudit('task_pause', { task_id: taskId });
                const res = await fetch(`/api/tasks/${encodeURIComponent(taskId)}/pause`, { method: 'POST' });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    alert(data.error || '暂停失败');
                }
            } else if (action === 'resume') {
                emitUiAudit('task_resume', { task_id: taskId });
                const res = await fetch(`/api/tasks/${encodeURIComponent(taskId)}/resume`, { method: 'POST' });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    alert(data.error || '继续失败');
                }
            } else if (action === 'stop') {
                emitUiAudit('task_stop', { task_id: taskId, source: 'projects' });
                const res = await fetch(`/api/tasks/${encodeURIComponent(taskId)}/stop`, { method: 'POST' });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    alert(data.error || '停止失败');
                }
            } else if (action === 'delete') {
                const ok = confirm(`确认删除任务：${taskId} ？该操作会清除历史日志。`);
                if (!ok) return;
                emitUiAudit('task_delete', { task_id: taskId });
                const res = await fetch(`/api/tasks/${encodeURIComponent(taskId)}`, { method: 'DELETE' });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    alert(data.error || '删除失败');
                    return;
                }
                projectsState.selectedTaskId = '';
                projectsState.lastEventId = 0;
                if (projectsDetailLog) projectsDetailLog.textContent = '';
                if (projectsDetailMeta) projectsDetailMeta.textContent = '请选择一个任务以查看日志。';
            }
            await refreshProjectsData();
            renderProjectsList(projectsState.tasks);
            if (projectsState.selectedTaskId) {
                await updateProjectsDetailMeta(projectsState.selectedTaskId);
            }
        }

        if (projectsStartBtn) projectsStartBtn.addEventListener('click', () => actionOnSelected('start'));
        if (projectsPauseBtn) projectsPauseBtn.addEventListener('click', () => actionOnSelected('pause'));
        if (projectsResumeBtn) projectsResumeBtn.addEventListener('click', () => actionOnSelected('resume'));
        if (projectsStopBtn) projectsStopBtn.addEventListener('click', () => actionOnSelected('stop'));
        if (projectsDeleteBtn) projectsDeleteBtn.addEventListener('click', () => actionOnSelected('delete'));
    }

    function formatAuditTs(tsSeconds) {
        try {
            const d = new Date((Number(tsSeconds) || 0) * 1000);
            return d.toLocaleString();
        } catch (e) {
            return '';
        }
    }

    function _auditPageName(pageId) {
        const p = String(pageId || '');
        const map = {
            'page-chat': '控制台',
            'page-projects': '项目管理',
            'page-attackchain': '攻击链',
            'page-recon': '信息收集',
            'page-vulns': '漏洞管理',
            'page-persistence': '权限维持',
            'page-loot': '文件管理',
            'page-lateralmove': '内网横向',
            'page-tasks': '扫描报告',
            'page-tools': '工具箱',
            'page-skills': 'Skills',
            'page-knowledge': '知识库',
            'page-vulndb': '漏洞库',
            'page-auditlog': '日志管理',
            'page-settings': '系统设置',
        };
        return map[p] || p || '—';
    }

    function _auditHumanize(row) {
        const action = String((row && row.action) || '').trim();
        const detail = (row && row.detail && typeof row.detail === 'object') ? row.detail : {};

        const isHttp = /^(GET|POST|PUT|DELETE)\s/i.test(action);
        if (isHttp) {
            return {
                type: '接口',
                op: action,
                obj: String(row.path || ''),
                summary: `${action}  ${String(row.path || '')}`,
            };
        }

        if (action === 'ui_event') {
            const ev = String(detail.event || '').trim();
            const d = (detail.detail && typeof detail.detail === 'object') ? detail.detail : {};
            const taskId = String(d.task_id || '').trim();

            const mk = (op, obj, extra) => ({
                type: '用户',
                op,
                obj,
                summary: [op, obj, extra].filter(Boolean).join('  ·  '),
            });

            if (ev === 'navigate') return mk('切换页面', _auditPageName(d.page), '');
            if (ev === 'chat_submit_target') return mk('提交目标', taskId || '—', d.source ? `来源:${d.source}` : '');
            if (ev === 'chat_select_task') return mk('切换当前项目', taskId || '—', '');

            if (ev === 'task_create') return mk('创建项目', taskId || '—', d.has_goal ? '含目标描述' : '');
            if (ev === 'task_start') return mk('启动项目', taskId || '—', d.source ? `来源:${d.source}` : '');
            if (ev === 'task_pause') return mk('暂停项目', taskId || '—', '');
            if (ev === 'task_resume') return mk('继续项目', taskId || '—', '');
            if (ev === 'task_stop') return mk('停止项目', taskId || '—', d.source ? `来源:${d.source}` : '');
            if (ev === 'task_delete') return mk('删除项目', taskId || '—', '');

            if (ev === 'attackchain_select_task') return mk('查看攻击链', taskId || '—', '');
            if (ev === 'attackchain_select_stage') return mk('选择攻击链阶段', taskId || '—', d.stage_id ? `阶段:${d.stage_id}` : '');

            if (ev === 'recon_select_task') return mk('查看信息收集', taskId || '—', '');
            if (ev === 'recon_select_step') return mk('选择信息收集步骤', taskId || '—', d.step_id ? `步骤:${d.step_id}` : '');

            if (ev === 'persistence_select_task') return mk('查看权限维持', taskId || '—', '');
            if (ev === 'persistence_select_step') return mk('选择权限维持步骤', taskId || '—', d.step_id ? `步骤:${d.step_id}` : '');

            if (ev === 'lateral_select_task') return mk('查看内网横向', taskId || '—', '');
            if (ev === 'lateral_select_step') return mk('选择内网横向步骤', taskId || '—', d.step_id ? `步骤:${d.step_id}` : '');

            if (ev === 'report_view') return mk('查看报告', String(d.filename || '').trim() || '—', '');
            if (ev === 'report_delete') return mk('删除报告', String(d.filename || '').trim() || '—', '');

            if (ev === 'export_vulns') return mk('导出漏洞清单', taskId || '—', d.count !== undefined ? `数量:${d.count}` : '');
            if (ev === 'vuln_view') return mk('查看漏洞', String(d.vuln_id || '').trim() || '—', taskId ? `项目:${taskId}` : '');
            if (ev === 'vuln_delete') return mk('删除漏洞', String(d.vuln_id || '').trim() || '—', taskId ? `项目:${taskId}` : '');

            if (ev === 'settings_save') return mk('保存系统设置', '—', '');

            if (ev === 'loot_select_task') return mk('打开文件库', taskId || '—', '');
            if (ev === 'loot_enter_dir') return mk('进入目录', taskId || '—', d.path ? `路径:${d.path}` : '');
            if (ev === 'loot_preview') return mk('预览文件', taskId || '—', d.path ? `路径:${d.path}` : '');
            if (ev === 'loot_upload') return mk('上传文件', taskId || '—', d.name ? `文件:${d.name}` : '');
            if (ev === 'loot_download') return mk('下载文件', taskId || '—', d.path ? `路径:${d.path}` : '');
            if (ev === 'loot_delete') return mk('删除文件/目录', taskId || '—', d.path ? `路径:${d.path}` : '');
            if (ev === 'loot_mkdir') return mk('新建文件夹', taskId || '—', d.path ? `路径:${d.path}` : '');
            if (ev === 'loot_remote_read') return mk('从会话读取文件', taskId || '—', (d.session_id ? `会话:${d.session_id}` : '') + (d.path ? ` 路径:${d.path}` : ''));
            if (ev === 'loot_remote_save') return mk('保存远程文件到文件库', taskId || '—', d.name ? `文件:${d.name}` : '');

            return mk(ev || '用户操作', taskId || '—', '');
        }

        const mkSys = (op, obj, extra) => ({
            type: '系统',
            op,
            obj,
            summary: [op, obj, extra].filter(Boolean).join('  ·  '),
        });
        if (action === 'task_create') return mkSys('项目创建', String(detail.task_id || '').trim() || '—', detail.exists ? '已存在' : '');
        if (action === 'task_start') return mkSys('项目启动', String(detail.task_id || '').trim() || '—', String(detail.status || '').trim());
        if (action === 'task_pause') return mkSys('项目暂停', String(detail.task_id || '').trim() || '—', '');
        if (action === 'task_resume') return mkSys('项目继续', String(detail.task_id || '').trim() || '—', '');
        if (action === 'task_stop') return mkSys('项目停止', String(detail.task_id || '').trim() || '—', String(detail.status || '').trim());
        if (action === 'task_delete') return mkSys('项目删除', String(detail.task_id || '').trim() || '—', '');
        if (action === 'update_config') return mkSys('保存系统设置', (Array.isArray(detail.changed_fields) && detail.changed_fields.length) ? `字段:${detail.changed_fields.join(',')}` : '—', '');
        if (action === 'vuln_upsert') return mkSys('漏洞更新', String(detail.vuln_id || '').trim() || '—', String(detail.severity || '').trim());
        if (action === 'vuln_delete') return mkSys('漏洞删除', String(detail.vuln_id || '').trim() || '—', '');
        if (action === 'loot_upload') return mkSys('文件上传', String(detail.task_id || '').trim() || '—', detail.path ? `路径:${detail.path}` : '');
        if (action === 'loot_download') return mkSys('文件下载', String(detail.task_id || '').trim() || '—', detail.path ? `路径:${detail.path}` : '');
        if (action === 'loot_delete') return mkSys('文件删除', String(detail.task_id || '').trim() || '—', detail.path ? `路径:${detail.path}` : '');
        if (action === 'loot_mkdir') return mkSys('创建目录', String(detail.task_id || '').trim() || '—', detail.path ? `路径:${detail.path}` : '');
        if (action === 'msf_read_file') return mkSys('会话读取文件', String(detail.task_id || '').trim() || '—', (detail.session_id ? `会话:${detail.session_id}` : '') + (detail.path ? ` 路径:${detail.path}` : ''));

        return mkSys(action || '系统操作', '—', '');
    }

    function renderAuditDetail(row) {
        if (!auditDetailMeta || !auditDetailRaw) return;
        if (!row) {
            auditDetailMeta.textContent = '—';
            auditDetailRaw.textContent = '选择一条日志查看详情。';
            return;
        }
        const h = _auditHumanize(row);
        const metaParts = [];
        if (row.id !== undefined) metaParts.push(`#${row.id}`);
        if (row.ts) metaParts.push(formatAuditTs(row.ts));
        if (h.type) metaParts.push(h.type);
        if (row.actor_ip) metaParts.push(row.actor_ip);
        auditDetailMeta.textContent = metaParts.join('  ·  ');
        try {
            const top = [
                `类型: ${h.type}`,
                `操作: ${h.op}`,
                `对象: ${h.obj || '—'}`,
            ].join('\n');
            auditDetailRaw.textContent = top + "\n\n---\n\n" + JSON.stringify(row, null, 2);
        } catch (e) {
            auditDetailRaw.textContent = String(row);
        }
    }

    function renderAuditList() {
        if (!auditLogList) return;
        auditLogList.innerHTML = '';
        const rows = auditState.logs || [];
        if (!rows.length) {
            const empty = document.createElement('div');
            empty.className = 'empty-state';
            empty.innerHTML = '<i class="fa-regular fa-folder-open"></i><p>暂无日志</p>';
            auditLogList.appendChild(empty);
            renderAuditDetail(null);
            if (auditPageHint) auditPageHint.textContent = `第 ${Math.floor(auditState.offset / auditState.limit) + 1} 页`;
            return;
        }

        const frag = document.createDocumentFragment();
        rows.forEach((r) => {
            const h = _auditHumanize(r);
            const row = document.createElement('div');
            row.className = 'audit-row' + (auditState.selectedId === r.id ? ' active' : '');
            row.dataset.id = String(r.id);

            const ts = document.createElement('div');
            ts.className = 'audit-cell small';
            try {
                ts.textContent = new Date((Number(r.ts) || 0) * 1000).toLocaleTimeString();
            } catch (e) {
                ts.textContent = '';
            }

            const kind = document.createElement('div');
            kind.className = 'audit-badge ok';
            kind.textContent = h.type || '';

            const op = document.createElement('div');
            op.className = 'audit-cell';
            op.textContent = h.op || '';

            const obj = document.createElement('div');
            obj.className = 'audit-cell small';
            obj.textContent = h.obj || '';

            const idBadge = document.createElement('div');
            idBadge.className = 'audit-badge ok';
            idBadge.textContent = `#${r.id}`;

            row.appendChild(ts);
            row.appendChild(kind);
            row.appendChild(op);
            row.appendChild(obj);
            row.appendChild(idBadge);

            row.addEventListener('click', () => {
                auditState.selectedId = r.id;
                renderAuditList();
                renderAuditDetail(r);
            });

            frag.appendChild(row);
        });
        auditLogList.appendChild(frag);

        if (auditPageHint) {
            const page = Math.floor(auditState.offset / auditState.limit) + 1;
            auditPageHint.textContent = `第 ${page} 页  ·  本页 ${rows.length} 条`;
        }

        if (!auditState.selectedId && rows[0]) {
            auditState.selectedId = rows[0].id;
            renderAuditDetail(rows[0]);
        }
    }

    async function loadAuditStats() {
        if (!auditStatsText) return;
        try {
            const res = await fetch('/api/audit/stats');
            const s = await res.json();
            if (!res.ok) return;
            const total = (s.total !== undefined) ? s.total : '--';
            const maxRows = (s.max_rows !== undefined) ? s.max_rows : '--';
            const oldest = s.oldest_ts ? formatAuditTs(s.oldest_ts) : '';
            const newest = s.newest_ts ? formatAuditTs(s.newest_ts) : '';
            auditStatsText.textContent = `总计 ${total} 条  ·  保留上限 ${maxRows} 条` + (newest ? `  ·  最新 ${newest}` : '') + (oldest ? `  ·  最早 ${oldest}` : '');
        } catch (e) {}
    }

    function _getAuditFilters() {
        const preset = auditActionPreset ? String(auditActionPreset.value || '').trim() : '';
        let action = auditActionInput ? String(auditActionInput.value || '').trim() : '';
        let path = auditPathInput ? String(auditPathInput.value || '').trim() : '';
        const adv = auditAdvancedKind ? String(auditAdvancedKind.value || '').trim() : '';
        const kind = adv || preset;
        return {
            q: auditQueryInput ? String(auditQueryInput.value || '').trim() : '',
            method: auditMethodSelect ? String(auditMethodSelect.value || '').trim() : '',
            path: path,
            action: action,
            kind: kind,
        };
    }

    async function loadAuditLogs(reset = false) {
        if (reset) {
            auditState.offset = 0;
            auditState.selectedId = 0;
        }
        const f = _getAuditFilters();
        const params = new URLSearchParams();
        params.set('limit', String(auditState.limit));
        params.set('offset', String(auditState.offset));
        if (f.q) params.set('q', f.q);
        if (f.method) params.set('method', f.method);
        if (f.path) params.set('path', f.path);
        if (f.action) params.set('action', f.action);
        if (f.kind) params.set('kind', f.kind);
        try {
            const res = await fetch(`/api/audit/logs?${params.toString()}`);
            const data = await res.json();
            if (!res.ok) return;
            auditState.logs = Array.isArray(data.logs) ? data.logs : [];
            renderAuditList();
        } catch (e) {}
    }

    function initAuditLogPage() {
        if (auditState.initialized) {
            loadAuditStats().then(() => {});
            loadAuditLogs(false).then(() => {});
            return;
        }
        auditState.initialized = true;
        loadAuditStats().then(() => {});
        loadAuditLogs(true).then(() => {});

        const scheduleReload = (() => {
            let t = null;
            return () => {
                if (t) clearTimeout(t);
                t = setTimeout(async () => {
                    await loadAuditStats();
                    await loadAuditLogs(true);
                }, 250);
            };
        })();

        if (refreshAuditBtn) refreshAuditBtn.addEventListener('click', async () => {
            await loadAuditStats();
            await loadAuditLogs(true);
        });

        if (auditQueryInput) auditQueryInput.addEventListener('input', scheduleReload);
        if (auditPathInput) auditPathInput.addEventListener('input', scheduleReload);
        if (auditActionInput) auditActionInput.addEventListener('input', scheduleReload);
        if (auditMethodSelect) auditMethodSelect.addEventListener('change', scheduleReload);
        if (auditActionPreset) auditActionPreset.addEventListener('change', scheduleReload);

        if (auditPrevBtn) auditPrevBtn.addEventListener('click', async () => {
            auditState.offset = Math.max(0, auditState.offset - auditState.limit);
            await loadAuditLogs(false);
        });
        if (auditNextBtn) auditNextBtn.addEventListener('click', async () => {
            if (!auditState.logs || auditState.logs.length < auditState.limit) return;
            auditState.offset += auditState.limit;
            await loadAuditLogs(false);
        });

        if (clearAuditBtn) clearAuditBtn.addEventListener('click', async () => {
            const ok = confirm('确认清空所有审计日志？该操作会被记录。');
            if (!ok) return;
            const reason = prompt('请输入清空原因（可留空）', '') || '';
            try {
                const res = await fetch('/api/audit/clear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reason: reason })
                });
                const data = await res.json().catch(() => ({}));
                if (!res.ok) {
                    alert(data.error || '清空失败');
                    return;
                }
                auditState.offset = 0;
                auditState.selectedId = 0;
                await loadAuditStats();
                await loadAuditLogs(true);
            } catch (e) {
                alert('清空失败');
            }
        });
    }

    function _parseToolArgsFromLog(content) {
        const s = String(content || '');
        const i = s.indexOf('参数:');
        if (i < 0) return null;
        const raw = s.slice(i + 3).trim();
        try {
            return JSON.parse(raw);
        } catch (e) {
            return raw;
        }
    }

    function _extractToolCallFromEventRow(row) {
        const ev = row && row.event ? row.event : {};
        if (ev.type !== 'log') return null;
        const content = String(ev.content || '');
        if (!content.startsWith('[工具调用]')) return null;
        const m = content.match(/^\[工具调用\]\s+([^\s]+)\s+参数:/);
        const tool = m ? m[1] : '';
        const args = _parseToolArgsFromLog(content);
        return { tool, args, raw: content };
    }

    function _extractToolResultFromEventRow(row) {
        const ev = row && row.event ? row.event : {};
        if (ev.type !== 'log') return null;
        const content = String(ev.content || '');
        if (!content.startsWith('[工具结果]')) return null;
        const m = content.match(/^\[工具结果\]\s+([^\s:]+)\s*:\s*([\s\S]*)$/);
        const tool = m ? m[1] : '';
        const body = m ? m[2] : content;
        return { tool, body, raw: content };
    }

    function _extractArtifactsFromText(text) {
        const s = String(text || '');
        const out = new Set();
        const win = s.match(/[A-Za-z]:\\[^\s"'<>|]{3,}/g) || [];
        win.forEach(p => out.add(p));
        const unix = s.match(/\/[^\s"'<>]{3,}/g) || [];
        unix.forEach(p => out.add(p));
        const url = s.match(/https?:\/\/[^\s"'<>]+/g) || [];
        url.forEach(p => out.add(p));
        return Array.from(out).slice(0, 80);
    }

    function _extractPersistInfoFromText(text, info) {
        const s = String(text || '');
        const out = info || {};
        const lines = s.split(/\r?\n/).map(x => x.trim()).filter(Boolean);

        for (const ln of lines) {
            if (!out.identity) {
                const m = ln.match(/^(?:whoami|current user|user)\s*[:=]\s*(.+)$/i);
                if (m) out.identity = m[1].trim();
            }
            if (!out.identity) {
                if (ln.includes('\\') && ln.length <= 120) out.identity = ln;
            }
            if (!out.hostname) {
                const m = ln.match(/^(?:hostname|host)\s*[:=]\s*(.+)$/i);
                if (m) out.hostname = m[1].trim();
            }
            if (!out.privs && /SeDebugPrivilege|SeImpersonatePrivilege|sudoers|uid=\d+/i.test(ln)) {
                out.privs = out.privs ? (out.privs + '\n' + ln) : ln;
            }
            if (!out.ip && /(IPv4 Address|inet\s+\d+\.\d+\.\d+\.\d+)/i.test(ln)) {
                out.ip = out.ip ? (out.ip + '\n' + ln) : ln;
            }
        }
        return out;
    }

    function _classifyPersistenceSteps(rows) {
        const steps = [];
        const tools = new Set();
        const artifacts = new Set();
        let info = {};
        let inPersist = false;

        for (const r of rows || []) {
            const ev = r && r.event ? r.event : {};
            const type = String(ev.type || '');
            const content = String(ev.content || '');
            if (type === 'log' && content.startsWith('[MOE]')) {
                inPersist = content.toLowerCase().includes('persistence');
                continue;
            }
            if (!inPersist) continue;

            const call = _extractToolCallFromEventRow(r);
            if (call && call.tool) {
                tools.add(call.tool);
                const args = call.args;
                const cmd = (() => {
                    if (!args) return '';
                    if (typeof args === 'string') return args;
                    const picks = [];
                    if (args.command) picks.push(String(args.command));
                    if (args.args) picks.push(String(args.args));
                    if (args.target) picks.push(`target=${args.target}`);
                    if (args.url) picks.push(`url=${args.url}`);
                    if (args.path) picks.push(`path=${args.path}`);
                    if (args.file) picks.push(`file=${args.file}`);
                    return picks.filter(Boolean).join('  ');
                })();
                _extractArtifactsFromText(JSON.stringify(args)).forEach(x => artifacts.add(x));
                steps.push({
                    id: r.id,
                    ts: r.ts,
                    kind: 'tool_call',
                    tool: call.tool,
                    cmd: cmd,
                    artifacts: _extractArtifactsFromText(cmd).concat(_extractArtifactsFromText(call.raw)),
                    row: r,
                });
                continue;
            }

            const res = _extractToolResultFromEventRow(r);
            if (res && res.tool) {
                tools.add(res.tool);
                _extractArtifactsFromText(res.body).forEach(x => artifacts.add(x));
                info = _extractPersistInfoFromText(res.body, info);
                steps.push({
                    id: r.id,
                    ts: r.ts,
                    kind: 'tool_result',
                    tool: res.tool,
                    cmd: '',
                    artifacts: _extractArtifactsFromText(res.body),
                    row: r,
                });
                continue;
            }

            if (type === 'thought' || type === 'error') {
                info = _extractPersistInfoFromText(content, info);
                _extractArtifactsFromText(content).forEach(x => artifacts.add(x));
                steps.push({
                    id: r.id,
                    ts: r.ts,
                    kind: type,
                    tool: '',
                    cmd: '',
                    artifacts: _extractArtifactsFromText(content),
                    row: r,
                });
            }
        }

        return {
            steps,
            tools: Array.from(tools).sort((a, b) => a.localeCompare(b)),
            artifacts: Array.from(artifacts).sort((a, b) => a.localeCompare(b)),
            info,
        };
    }

    function _extractIpv4FromText(text) {
        const s = String(text || '');
        const out = new Set();
        const matches = s.match(/\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b/g) || [];
        matches.forEach(ip => out.add(ip));
        return Array.from(out).slice(0, 200);
    }

    function _extractHostnamesFromText(text) {
        const s = String(text || '');
        const out = new Set();
        const matches = s.match(/\b[a-zA-Z0-9][a-zA-Z0-9-]{0,62}(?:\.[a-zA-Z0-9][a-zA-Z0-9-]{0,62})+\b/g) || [];
        matches.forEach(h => {
            const lh = h.toLowerCase();
            if (lh.endsWith('.local') || lh.endsWith('.lan') || lh.endsWith('.corp') || lh.endsWith('.internal') || lh.endsWith('.intra') || lh.includes('.ad.')) {
                out.add(h);
            }
        });
        return Array.from(out).slice(0, 200);
    }

    function _extractCredHintsFromText(text) {
        const s = String(text || '');
        const out = [];
        const lines = s.split(/\r?\n/).slice(0, 400);
        for (const ln of lines) {
            if (/password\s*[:=]|passwd\s*[:=]|hash\s*[:=]|ntlm|krbtgt|ticket|kerberos|tgt|tdc|ccache|\.kirbi|id_rsa|private key|sshpass|apikey|token/i.test(ln)) {
                const trimmed = ln.trim();
                if (trimmed.length >= 4) out.push(trimmed.slice(0, 240));
            }
        }
        return out.slice(0, 40);
    }

    function _extractLateralInfoFromText(text, info) {
        const s = String(text || '');
        const out = info || {};
        out.hosts = Array.isArray(out.hosts) ? out.hosts : [];
        out.subnets = Array.isArray(out.subnets) ? out.subnets : [];
        out.identities = Array.isArray(out.identities) ? out.identities : [];
        out.privileges = Array.isArray(out.privileges) ? out.privileges : [];
        out.creds = Array.isArray(out.creds) ? out.creds : [];
        out.notes = Array.isArray(out.notes) ? out.notes : [];

        const ips = _extractIpv4FromText(s);
        ips.forEach(ip => {
            if (!out.hosts.includes(ip)) out.hosts.push(ip);
        });
        const hosts = _extractHostnamesFromText(s);
        hosts.forEach(h => {
            if (!out.hosts.includes(h)) out.hosts.push(h);
        });

        const subnetMatches = s.match(/\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}0\/\d{1,2}\b/g) || [];
        subnetMatches.forEach(sn => {
            if (!out.subnets.includes(sn)) out.subnets.push(sn);
        });

        const idMatches = s.match(/\b[a-zA-Z0-9._-]+\\[a-zA-Z0-9.$_-]+\b/g) || [];
        idMatches.forEach(id => {
            if (!out.identities.includes(id)) out.identities.push(id);
        });
        const whoami = s.match(/^(?:whoami|current user|user)\s*[:=]\s*(.+)$/im);
        if (whoami && whoami[1]) {
            const v = whoami[1].trim();
            if (v && !out.identities.includes(v)) out.identities.push(v);
        }

        const privLines = [];
        const lines = s.split(/\r?\n/).slice(0, 500);
        for (const ln of lines) {
            if (/SeDebugPrivilege|SeImpersonatePrivilege|SeTcbPrivilege|sudoers|uid=\d+|admin group|Domain Admin|Enterprise Admin/i.test(ln)) {
                privLines.push(ln.trim().slice(0, 220));
            }
        }
        privLines.slice(0, 30).forEach(p => {
            if (!out.privileges.includes(p)) out.privileges.push(p);
        });

        _extractCredHintsFromText(s).forEach(c => {
            if (!out.creds.includes(c)) out.creds.push(c);
        });

        if (/psexec|wmiexec|smbexec|winrm|evil-winrm|rpcclient|crackmapexec|netexec|impacket|ssh\s|scp\s|smbclient|xfreerdp|rdesktop|mimikatz/i.test(s)) {
            const hint = s.match(/^(.*(?:psexec|wmiexec|smbexec|winrm|evil-winrm|rpcclient|crackmapexec|netexec|impacket|ssh|scp|smbclient|xfreerdp|rdesktop|mimikatz).*)$/im);
            if (hint && hint[1]) out.notes.push(hint[1].trim().slice(0, 240));
        }

        out.hosts = out.hosts.slice(0, 200);
        out.subnets = out.subnets.slice(0, 80);
        out.identities = out.identities.slice(0, 80);
        out.privileges = out.privileges.slice(0, 80);
        out.creds = out.creds.slice(0, 80);
        out.notes = out.notes.slice(0, 80);
        return out;
    }

    function _isLateralMoeLog(content) {
        const s = String(content || '').toLowerCase();
        if (!s.startsWith('[moe]')) return false;
        return s.includes('lateral') || s.includes('movement') || s.includes('lateralmove') || s.includes('pivot') || s.includes('内网横向');
    }

    function _classifyLateralSteps(rows) {
        const steps = [];
        const tools = new Set();
        const artifacts = new Set();
        let info = {};
        let inLateral = false;

        for (const r of rows || []) {
            const ev = r && r.event ? r.event : {};
            const type = String(ev.type || '');
            const content = String(ev.content || '');
            if (type === 'log' && _isLateralMoeLog(content)) {
                inLateral = true;
                continue;
            }
            if (type === 'log' && content.startsWith('[MOE]') && !_isLateralMoeLog(content)) {
                inLateral = false;
                continue;
            }
            if (!inLateral) continue;

            const call = _extractToolCallFromEventRow(r);
            if (call && call.tool) {
                tools.add(call.tool);
                const args = call.args;
                const cmd = (() => {
                    if (!args) return '';
                    if (typeof args === 'string') return args;
                    const picks = [];
                    if (args.command) picks.push(String(args.command));
                    if (args.args) picks.push(String(args.args));
                    if (args.target) picks.push(`target=${args.target}`);
                    if (args.url) picks.push(`url=${args.url}`);
                    if (args.host) picks.push(`host=${args.host}`);
                    if (args.ip) picks.push(`ip=${args.ip}`);
                    if (args.username) picks.push(`user=${args.username}`);
                    if (args.domain) picks.push(`domain=${args.domain}`);
                    if (args.hash) picks.push(`hash=${String(args.hash).slice(0, 32)}…`);
                    if (args.password) picks.push('password=***');
                    return picks.filter(Boolean).join('  ');
                })();
                const argArtifacts = _extractArtifactsFromText(JSON.stringify(args));
                argArtifacts.forEach(x => artifacts.add(x));
                info = _extractLateralInfoFromText(JSON.stringify(args), info);
                steps.push({
                    id: r.id,
                    ts: r.ts,
                    kind: 'tool_call',
                    tool: call.tool,
                    cmd: cmd,
                    artifacts: _extractArtifactsFromText(cmd).concat(_extractArtifactsFromText(call.raw)).concat(argArtifacts),
                    row: r,
                });
                continue;
            }

            const res = _extractToolResultFromEventRow(r);
            if (res && res.tool) {
                tools.add(res.tool);
                const a = _extractArtifactsFromText(res.body);
                a.forEach(x => artifacts.add(x));
                info = _extractLateralInfoFromText(res.body, info);
                steps.push({
                    id: r.id,
                    ts: r.ts,
                    kind: 'tool_result',
                    tool: res.tool,
                    cmd: '',
                    artifacts: a,
                    row: r,
                });
                continue;
            }

            if (type === 'thought' || type === 'error') {
                const a = _extractArtifactsFromText(content);
                a.forEach(x => artifacts.add(x));
                info = _extractLateralInfoFromText(content, info);
                steps.push({
                    id: r.id,
                    ts: r.ts,
                    kind: type,
                    tool: '',
                    cmd: '',
                    artifacts: a,
                    row: r,
                });
            }
        }

        return {
            steps,
            tools: Array.from(tools).sort((a, b) => a.localeCompare(b)),
            artifacts: Array.from(artifacts).sort((a, b) => a.localeCompare(b)),
            info,
        };
    }

    function _classifyReconSteps(rows) {
        const steps = [];
        const tools = new Set();
        let inRecon = false;

        for (const r of rows || []) {
            const ev = r && r.event ? r.event : {};
            const type = String(ev.type || '');
            const content = String(ev.content || '');
            if (type === 'log' && content.startsWith('[MOE]')) {
                inRecon = content.toLowerCase().includes('reconnaissance');
                continue;
            }
            if (!inRecon) continue;

            const call = _extractToolCallFromEventRow(r);
            if (call && call.tool) {
                tools.add(call.tool);
                const cmd = (() => {
                    if (!call.args) return '';
                    if (typeof call.args === 'string') return call.args;
                    const picks = [];
                    if (call.args.command) picks.push(String(call.args.command));
                    if (call.args.args) picks.push(String(call.args.args));
                    if (call.args.target) picks.push(`target=${call.args.target}`);
                    if (call.args.url) picks.push(`url=${call.args.url}`);
                    if (call.args.resource_script) picks.push(`rc=${call.args.resource_script}`);
                    return picks.filter(Boolean).join('  ');
                })();
                steps.push({
                    id: r.id,
                    ts: r.ts,
                    kind: 'tool_call',
                    tool: call.tool,
                    cmd: cmd,
                    raw: call.raw,
                    row: r,
                });
                continue;
            }

            const res = _extractToolResultFromEventRow(r);
            if (res && res.tool) {
                tools.add(res.tool);
                steps.push({
                    id: r.id,
                    ts: r.ts,
                    kind: 'tool_result',
                    tool: res.tool,
                    cmd: '',
                    raw: res.raw,
                    row: r,
                });
                continue;
            }

            if (type === 'thought' || type === 'error') {
                steps.push({
                    id: r.id,
                    ts: r.ts,
                    kind: type,
                    tool: '',
                    cmd: '',
                    raw: String(ev.content || ''),
                    row: r,
                });
            }
        }

        return { steps, tools: Array.from(tools).sort((a, b) => a.localeCompare(b)) };
    }

    function renderRecon() {
        if (!reconStepList || !reconSummary || !reconToolTags) return;
        const hasTask = Boolean(reconState.taskId);
        if (!hasTask) {
            reconSummary.textContent = '请选择一个项目/任务以查看信息收集过程。';
            reconToolTags.innerHTML = '';
            reconStepList.innerHTML = '';
            if (reconDetailMeta) reconDetailMeta.textContent = '—';
            if (reconDetailTool) reconDetailTool.textContent = '—';
            if (reconDetailCmd) reconDetailCmd.textContent = '—';
            if (reconDetailRaw) reconDetailRaw.textContent = '选择一条步骤以查看完整输出。';
            return;
        }

        const total = reconState.steps.length;
        const toolCount = new Set(reconState.steps.map(s => s.tool).filter(Boolean)).size;
        const lastTs = total ? (reconState.steps[total - 1].ts || 0) : 0;
        reconSummary.textContent = `项目/任务：${reconState.taskId}  ·  步骤：${total}  ·  工具：${toolCount}` + (lastTs ? `  ·  最新：${formatTs(lastTs)}` : '');

        reconToolTags.innerHTML = '';
        const tags = reconState.tools || [];
        if (!tags.length) {
            const tag = document.createElement('div');
            tag.className = 'attack-chain-tool-tag';
            tag.textContent = '—';
            reconToolTags.appendChild(tag);
        } else {
            tags.slice(0, 30).forEach(tn => {
                const tag = document.createElement('div');
                tag.className = 'attack-chain-tool-tag';
                tag.textContent = tn;
                tag.addEventListener('click', () => {
                    const found = (reconState.steps || []).find(s => s && s.tool === tn);
                    if (found) {
                        reconState.selectedStepId = found.id;
                        renderRecon();
                        renderReconDetail(found);
                    }
                });
                reconToolTags.appendChild(tag);
            });
        }

        reconStepList.innerHTML = '';
        const frag = document.createDocumentFragment();
        reconState.steps.forEach((s) => {
            const row = document.createElement('div');
            row.className = 'audit-row' + (reconState.selectedStepId === s.id ? ' active' : '');
            row.dataset.id = String(s.id);

            const ts = document.createElement('div');
            ts.className = 'audit-cell small';
            try {
                ts.textContent = new Date((Number(s.ts) || 0) * 1000).toLocaleTimeString();
            } catch (e) {
                ts.textContent = '';
            }

            const kind = document.createElement('div');
            kind.className = 'audit-cell';
            kind.textContent = s.kind === 'tool_call' ? '调用' : (s.kind === 'tool_result' ? '结果' : s.kind);

            const tool = document.createElement('div');
            tool.className = 'audit-cell';
            tool.textContent = s.tool || '';

            const cmd = document.createElement('div');
            cmd.className = 'audit-cell small';
            cmd.textContent = s.cmd || (s.raw ? (String(s.raw).slice(0, 120) + (String(s.raw).length > 120 ? '…' : '')) : '');

            const badge = document.createElement('div');
            badge.className = 'audit-badge ok';
            badge.textContent = `#${s.id}`;

            row.appendChild(ts);
            row.appendChild(kind);
            row.appendChild(tool);
            row.appendChild(cmd);
            row.appendChild(badge);

            row.addEventListener('click', () => {
                reconState.selectedStepId = s.id;
                if (reconState.taskId) {
                    emitUiAudit('recon_select_step', { task_id: reconState.taskId, step_id: s.id, kind: s.kind, tool: s.tool || '' });
                }
                renderRecon();
                renderReconDetail(s);
            });

            frag.appendChild(row);
        });
        reconStepList.appendChild(frag);

        if (!reconState.selectedStepId && reconState.steps[0]) {
            reconState.selectedStepId = reconState.steps[0].id;
            renderReconDetail(reconState.steps[0]);
        }
    }

    function renderReconDetail(step) {
        if (!step) return;
        if (reconDetailMeta) {
            const parts = [];
            if (step.id) parts.push(`#${step.id}`);
            if (step.ts) parts.push(formatTs(step.ts));
            if (step.kind) parts.push(step.kind);
            reconDetailMeta.textContent = parts.join('  ·  ');
        }
        if (reconDetailTool) reconDetailTool.textContent = step.tool || '—';
        if (reconDetailCmd) reconDetailCmd.textContent = step.cmd || '—';
        if (reconDetailRaw) {
            try {
                const ev = step.row && step.row.event ? step.row.event : {};
                if (ev && ev.content) {
                    reconDetailRaw.textContent = String(ev.content);
                } else {
                    reconDetailRaw.textContent = JSON.stringify(step.row, null, 2);
                }
            } catch (e) {
                reconDetailRaw.textContent = String(step.raw || '');
            }
        }
    }

    async function loadReconTasks() {
        if (!reconTaskSelect) return;
        try {
            const tasks = await fetchTasks(200);
            const current = reconTaskSelect.value;
            reconTaskSelect.innerHTML = '<option value=\"\">选择项目/任务...</option>';
            (tasks || []).forEach(t => {
                if (!t || !t.task_id) return;
                const opt = document.createElement('option');
                opt.value = String(t.task_id);
                const st = statusLabel(t.status);
                opt.textContent = `${t.task_id}  ·  ${st.text}`;
                reconTaskSelect.appendChild(opt);
            });
            if (current) reconTaskSelect.value = current;
        } catch (e) {}
    }

    async function loadReconEvents(taskId, reset = false) {
        if (!taskId) return;
        const sinceId = reset ? 0 : (reconState.lastEventId || 0);
        try {
            const meta = await loadTaskMeta(taskId);
            reconState.taskMeta = meta;
        } catch (e) {
            reconState.taskMeta = null;
        }
        try {
            const rows = await loadTaskEvents(taskId, sinceId, 8000);
            if (reset) {
                reconState.events = rows;
            } else if (rows.length) {
                reconState.events = (reconState.events || []).concat(rows);
            }
            if (reconState.events.length) {
                const last = reconState.events[reconState.events.length - 1];
                if (last && last.id) reconState.lastEventId = last.id;
            }
            const classified = _classifyReconSteps(reconState.events);
            reconState.steps = classified.steps;
            reconState.tools = classified.tools;
            renderRecon();
        } catch (e) {}
    }

    function stopReconTimer() {
        if (reconState.timer) {
            clearInterval(reconState.timer);
            reconState.timer = null;
        }
    }

    function startReconTimer() {
        stopReconTimer();
        reconState.timer = setInterval(() => {
            if (!reconAutoRefresh || !reconAutoRefresh.checked) return;
            if (!reconState.taskId) return;
            loadReconEvents(reconState.taskId, false);
        }, 1500);
    }

    function initReconPage() {
        if (reconState.initialized) {
            startReconTimer();
            loadReconTasks().then(() => {});
            return;
        }
        reconState.initialized = true;
        loadReconTasks().then(() => {});
        renderRecon();

        if (reconTaskSelect) {
            reconTaskSelect.addEventListener('change', async () => {
                const taskId = String(reconTaskSelect.value || '').trim();
                reconState.taskId = taskId;
                reconState.lastEventId = 0;
                reconState.events = [];
                reconState.steps = [];
                reconState.selectedStepId = 0;
                renderRecon();
                if (taskId) {
                    emitUiAudit('recon_select_task', { task_id: taskId });
                    await loadReconEvents(taskId, true);
                }
            });
        }
        if (reconRefreshBtn) {
            reconRefreshBtn.addEventListener('click', async () => {
                await loadReconTasks();
                if (reconState.taskId) await loadReconEvents(reconState.taskId, true);
            });
        }
        if (reconAutoRefresh) {
            reconAutoRefresh.addEventListener('change', () => {
                startReconTimer();
            });
        }
        startReconTimer();
    }

    function renderPersistence() {
        if (!persistStepList || !persistSummary || !persistToolTags) return;
        const hasTask = Boolean(persistState.taskId);
        if (!hasTask) {
            persistSummary.textContent = '请选择一个项目/任务以查看权限维持过程。';
            if (persistInfoBadge) persistInfoBadge.textContent = '权限/信息：—';
            if (persistArtifactsBadge) persistArtifactsBadge.textContent = '工具/文件：—';
            persistToolTags.innerHTML = '';
            persistStepList.innerHTML = '';
            if (persistDetailMeta) persistDetailMeta.textContent = '—';
            if (persistDetailTool) persistDetailTool.textContent = '—';
            if (persistDetailCmd) persistDetailCmd.textContent = '—';
            if (persistDetailArtifacts) persistDetailArtifacts.textContent = '—';
            if (persistInfoBox) persistInfoBox.textContent = '—';
            if (persistDetailRaw) persistDetailRaw.textContent = '选择一条步骤以查看完整输出。';
            return;
        }

        const total = persistState.steps.length;
        const toolCount = new Set(persistState.steps.map(s => s.tool).filter(Boolean)).size;
        const artifactCount = Array.isArray(persistState.artifacts) ? persistState.artifacts.length : 0;
        const lastTs = total ? (persistState.steps[total - 1].ts || 0) : 0;
        persistSummary.textContent = `项目/任务：${persistState.taskId}  ·  步骤：${total}  ·  工具：${toolCount}` + (lastTs ? `  ·  最新：${formatTs(lastTs)}` : '');
        if (persistArtifactsBadge) persistArtifactsBadge.textContent = `工具/文件：${artifactCount}`;
        if (persistInfoBadge) {
            const keys = persistState.info ? Object.keys(persistState.info).length : 0;
            persistInfoBadge.textContent = `权限/信息：${keys ? keys + '项' : '—'}`;
        }

        persistToolTags.innerHTML = '';
        const tags = persistState.tools || [];
        if (!tags.length) {
            const tag = document.createElement('div');
            tag.className = 'attack-chain-tool-tag';
            tag.textContent = '—';
            persistToolTags.appendChild(tag);
        } else {
            tags.slice(0, 30).forEach(tn => {
                const tag = document.createElement('div');
                tag.className = 'attack-chain-tool-tag';
                tag.textContent = tn;
                tag.addEventListener('click', () => {
                    const found = (persistState.steps || []).find(s => s && s.tool === tn);
                    if (found) {
                        persistState.selectedStepId = found.id;
                        renderPersistence();
                        renderPersistenceDetail(found);
                    }
                });
                persistToolTags.appendChild(tag);
            });
        }

        if (persistInfoBox) {
            try {
                persistInfoBox.textContent = JSON.stringify(persistState.info || {}, null, 2);
            } catch (e) {
                persistInfoBox.textContent = String(persistState.info || '—');
            }
        }

        persistStepList.innerHTML = '';
        const frag = document.createDocumentFragment();
        persistState.steps.forEach((s) => {
            const row = document.createElement('div');
            row.className = 'audit-row' + (persistState.selectedStepId === s.id ? ' active' : '');
            row.dataset.id = String(s.id);

            const ts = document.createElement('div');
            ts.className = 'audit-cell small';
            try {
                ts.textContent = new Date((Number(s.ts) || 0) * 1000).toLocaleTimeString();
            } catch (e) {
                ts.textContent = '';
            }

            const kind = document.createElement('div');
            kind.className = 'audit-cell';
            kind.textContent = s.kind === 'tool_call' ? '调用' : (s.kind === 'tool_result' ? '结果' : s.kind);

            const tool = document.createElement('div');
            tool.className = 'audit-cell';
            tool.textContent = s.tool || '';

            const cmd = document.createElement('div');
            cmd.className = 'audit-cell small';
            const raw = s.cmd || '';
            cmd.textContent = raw ? (raw.slice(0, 120) + (raw.length > 120 ? '…' : '')) : '';

            const badge = document.createElement('div');
            badge.className = 'audit-badge ok';
            badge.textContent = `#${s.id}`;

            row.appendChild(ts);
            row.appendChild(kind);
            row.appendChild(tool);
            row.appendChild(cmd);
            row.appendChild(badge);

            row.addEventListener('click', () => {
                persistState.selectedStepId = s.id;
                if (persistState.taskId) {
                    emitUiAudit('persistence_select_step', { task_id: persistState.taskId, step_id: s.id, kind: s.kind, tool: s.tool || '' });
                }
                renderPersistence();
                renderPersistenceDetail(s);
            });

            frag.appendChild(row);
        });
        persistStepList.appendChild(frag);

        if (!persistState.selectedStepId && persistState.steps[0]) {
            persistState.selectedStepId = persistState.steps[0].id;
            renderPersistenceDetail(persistState.steps[0]);
        }
    }

    function renderPersistenceDetail(step) {
        if (!step) return;
        if (persistDetailMeta) {
            const parts = [];
            if (step.id) parts.push(`#${step.id}`);
            if (step.ts) parts.push(formatTs(step.ts));
            if (step.kind) parts.push(step.kind);
            persistDetailMeta.textContent = parts.join('  ·  ');
        }
        if (persistDetailTool) persistDetailTool.textContent = step.tool || '—';
        if (persistDetailCmd) persistDetailCmd.textContent = step.cmd || '—';
        if (persistDetailArtifacts) {
            const a = Array.isArray(step.artifacts) ? step.artifacts : [];
            persistDetailArtifacts.textContent = a.length ? a.slice(0, 12).join('\n') : '—';
        }
        if (persistDetailRaw) {
            try {
                const ev = step.row && step.row.event ? step.row.event : {};
                if (ev && ev.content) {
                    persistDetailRaw.textContent = String(ev.content);
                } else {
                    persistDetailRaw.textContent = JSON.stringify(step.row, null, 2);
                }
            } catch (e) {
                persistDetailRaw.textContent = '—';
            }
        }
    }

    async function loadPersistenceTasks() {
        if (!persistTaskSelect) return;
        try {
            const tasks = await fetchTasks(200);
            const current = persistTaskSelect.value;
            persistTaskSelect.innerHTML = '<option value=\"\">选择项目/任务...</option>';
            (tasks || []).forEach(t => {
                if (!t || !t.task_id) return;
                const opt = document.createElement('option');
                opt.value = String(t.task_id);
                const st = statusLabel(t.status);
                opt.textContent = `${t.task_id}  ·  ${st.text}`;
                persistTaskSelect.appendChild(opt);
            });
            if (current) persistTaskSelect.value = current;
        } catch (e) {}
    }

    async function loadPersistenceEvents(taskId, reset = false) {
        if (!taskId) return;
        const sinceId = reset ? 0 : (persistState.lastEventId || 0);
        try {
            const meta = await loadTaskMeta(taskId);
            persistState.taskMeta = meta;
        } catch (e) {
            persistState.taskMeta = null;
        }
        try {
            const rows = await loadTaskEvents(taskId, sinceId, 10000);
            if (reset) {
                persistState.events = rows;
            } else if (rows.length) {
                persistState.events = (persistState.events || []).concat(rows);
            }
            if (persistState.events.length) {
                const last = persistState.events[persistState.events.length - 1];
                if (last && last.id) persistState.lastEventId = last.id;
            }
            const classified = _classifyPersistenceSteps(persistState.events);
            persistState.steps = classified.steps;
            persistState.tools = classified.tools;
            persistState.artifacts = classified.artifacts;
            persistState.info = classified.info;
            renderPersistence();
        } catch (e) {}
    }

    function stopPersistenceTimer() {
        if (persistState.timer) {
            clearInterval(persistState.timer);
            persistState.timer = null;
        }
    }

    function startPersistenceTimer() {
        stopPersistenceTimer();
        persistState.timer = setInterval(() => {
            if (!persistAutoRefresh || !persistAutoRefresh.checked) return;
            if (!persistState.taskId) return;
            loadPersistenceEvents(persistState.taskId, false);
        }, 1500);
    }

    function initPersistencePage() {
        if (persistState.initialized) {
            startPersistenceTimer();
            loadPersistenceTasks().then(() => {});
            return;
        }
        persistState.initialized = true;
        loadPersistenceTasks().then(() => {});
        renderPersistence();

        if (persistTaskSelect) {
            persistTaskSelect.addEventListener('change', async () => {
                const taskId = String(persistTaskSelect.value || '').trim();
                persistState.taskId = taskId;
                persistState.lastEventId = 0;
                persistState.events = [];
                persistState.steps = [];
                persistState.tools = [];
                persistState.artifacts = [];
                persistState.info = {};
                persistState.selectedStepId = 0;
                renderPersistence();
                if (taskId) {
                    emitUiAudit('persistence_select_task', { task_id: taskId });
                    await loadPersistenceEvents(taskId, true);
                }
            });
        }
        if (persistRefreshBtn) {
            persistRefreshBtn.addEventListener('click', async () => {
                await loadPersistenceTasks();
                if (persistState.taskId) await loadPersistenceEvents(persistState.taskId, true);
            });
        }
        if (persistAutoRefresh) {
            persistAutoRefresh.addEventListener('change', () => {
                startPersistenceTimer();
            });
        }
        startPersistenceTimer();
    }

    function renderLateral() {
        if (!lateralStepList || !lateralSummary || !lateralToolTags) return;
        const hasTask = Boolean(lateralState.taskId);
        if (!hasTask) {
            lateralSummary.textContent = '请选择一个项目/任务以查看内网横向过程。';
            if (lateralPrivBadge) lateralPrivBadge.textContent = '权限/身份：—';
            if (lateralCredBadge) lateralCredBadge.textContent = '凭据：—';
            if (lateralHostBadge) lateralHostBadge.textContent = '主机/网段：—';
            if (lateralArtifactsBadge) lateralArtifactsBadge.textContent = '工具/文件：—';
            lateralToolTags.innerHTML = '';
            lateralStepList.innerHTML = '';
            if (lateralDetailMeta) lateralDetailMeta.textContent = '—';
            if (lateralDetailTool) lateralDetailTool.textContent = '—';
            if (lateralDetailCmd) lateralDetailCmd.textContent = '—';
            if (lateralDetailArtifacts) lateralDetailArtifacts.textContent = '—';
            if (lateralInfoBox) lateralInfoBox.textContent = '—';
            if (lateralDetailRaw) lateralDetailRaw.textContent = '选择一条步骤以查看完整输出。';
            return;
        }

        const total = lateralState.steps.length;
        const toolCount = new Set(lateralState.steps.map(s => s.tool).filter(Boolean)).size;
        const artifactCount = Array.isArray(lateralState.artifacts) ? lateralState.artifacts.length : 0;
        const lastTs = total ? (lateralState.steps[total - 1].ts || 0) : 0;
        lateralSummary.textContent = `项目/任务：${lateralState.taskId}  ·  步骤：${total}  ·  工具：${toolCount}` + (lastTs ? `  ·  最新：${formatTs(lastTs)}` : '');

        const info = lateralState.info || {};
        const idCount = Array.isArray(info.identities) ? info.identities.length : 0;
        const privCount = Array.isArray(info.privileges) ? info.privileges.length : 0;
        const credCount = Array.isArray(info.creds) ? info.creds.length : 0;
        const hostCount = Array.isArray(info.hosts) ? info.hosts.length : 0;
        const subnetCount = Array.isArray(info.subnets) ? info.subnets.length : 0;
        if (lateralPrivBadge) lateralPrivBadge.textContent = `权限/身份：${idCount ? idCount + '身份' : '—'}${privCount ? ' · ' + privCount + '权限' : ''}`;
        if (lateralCredBadge) lateralCredBadge.textContent = `凭据：${credCount || '—'}`;
        if (lateralHostBadge) lateralHostBadge.textContent = `主机/网段：${hostCount || '—'}${subnetCount ? ' · ' + subnetCount + '网段' : ''}`;
        if (lateralArtifactsBadge) lateralArtifactsBadge.textContent = `工具/文件：${artifactCount || '—'}`;

        lateralToolTags.innerHTML = '';
        const tags = lateralState.tools || [];
        if (!tags.length) {
            const tag = document.createElement('div');
            tag.className = 'attack-chain-tool-tag';
            tag.textContent = '—';
            lateralToolTags.appendChild(tag);
        } else {
            tags.slice(0, 30).forEach(tn => {
                const tag = document.createElement('div');
                tag.className = 'attack-chain-tool-tag';
                tag.textContent = tn;
                tag.addEventListener('click', () => {
                    const found = (lateralState.steps || []).find(s => s && s.tool === tn);
                    if (found) {
                        lateralState.selectedStepId = found.id;
                        renderLateral();
                        renderLateralDetail(found);
                    }
                });
                lateralToolTags.appendChild(tag);
            });
        }

        if (lateralInfoBox) {
            try {
                lateralInfoBox.textContent = JSON.stringify(info || {}, null, 2);
            } catch (e) {
                lateralInfoBox.textContent = String(info || '—');
            }
        }

        lateralStepList.innerHTML = '';
        const frag = document.createDocumentFragment();
        lateralState.steps.forEach((s) => {
            const row = document.createElement('div');
            row.className = 'audit-row' + (lateralState.selectedStepId === s.id ? ' active' : '');
            row.dataset.id = String(s.id);

            const ts = document.createElement('div');
            ts.className = 'audit-cell small';
            try {
                ts.textContent = new Date((Number(s.ts) || 0) * 1000).toLocaleTimeString();
            } catch (e) {
                ts.textContent = '';
            }

            const kind = document.createElement('div');
            kind.className = 'audit-cell';
            kind.textContent = s.kind === 'tool_call' ? '调用' : (s.kind === 'tool_result' ? '结果' : s.kind);

            const tool = document.createElement('div');
            tool.className = 'audit-cell';
            tool.textContent = s.tool || '';

            const cmd = document.createElement('div');
            cmd.className = 'audit-cell small';
            const raw = s.cmd || '';
            cmd.textContent = raw ? (raw.slice(0, 120) + (raw.length > 120 ? '…' : '')) : '';

            const badge = document.createElement('div');
            badge.className = 'audit-badge ok';
            badge.textContent = `#${s.id}`;

            row.appendChild(ts);
            row.appendChild(kind);
            row.appendChild(tool);
            row.appendChild(cmd);
            row.appendChild(badge);

            row.addEventListener('click', () => {
                lateralState.selectedStepId = s.id;
                if (lateralState.taskId) {
                    emitUiAudit('lateral_select_step', { task_id: lateralState.taskId, step_id: s.id, kind: s.kind, tool: s.tool || '' });
                }
                renderLateral();
                renderLateralDetail(s);
            });

            frag.appendChild(row);
        });
        lateralStepList.appendChild(frag);

        if (!lateralState.selectedStepId && lateralState.steps[0]) {
            lateralState.selectedStepId = lateralState.steps[0].id;
            renderLateralDetail(lateralState.steps[0]);
        }
    }

    function renderLateralDetail(step) {
        if (!step) return;
        if (lateralDetailMeta) {
            const parts = [];
            if (step.id) parts.push(`#${step.id}`);
            if (step.ts) parts.push(formatTs(step.ts));
            if (step.kind) parts.push(step.kind);
            lateralDetailMeta.textContent = parts.join('  ·  ');
        }
        if (lateralDetailTool) lateralDetailTool.textContent = step.tool || '—';
        if (lateralDetailCmd) lateralDetailCmd.textContent = step.cmd || '—';
        if (lateralDetailArtifacts) {
            const a = Array.isArray(step.artifacts) ? step.artifacts : [];
            lateralDetailArtifacts.textContent = a.length ? a.slice(0, 14).join('\n') : '—';
        }
        if (lateralDetailRaw) {
            try {
                const ev = step.row && step.row.event ? step.row.event : {};
                if (ev && ev.content) {
                    lateralDetailRaw.textContent = String(ev.content);
                } else {
                    lateralDetailRaw.textContent = JSON.stringify(step.row, null, 2);
                }
            } catch (e) {
                lateralDetailRaw.textContent = '—';
            }
        }
    }

    async function loadLateralTasks() {
        if (!lateralTaskSelect) return;
        try {
            const tasks = await fetchTasks(200);
            const current = lateralTaskSelect.value;
            lateralTaskSelect.innerHTML = '<option value=\"\">选择项目/任务...</option>';
            (tasks || []).forEach(t => {
                if (!t || !t.task_id) return;
                const opt = document.createElement('option');
                opt.value = String(t.task_id);
                const st = statusLabel(t.status);
                opt.textContent = `${t.task_id}  ·  ${st.text}`;
                lateralTaskSelect.appendChild(opt);
            });
            if (current) lateralTaskSelect.value = current;
        } catch (e) {}
    }

    async function loadLateralEvents(taskId, reset = false) {
        if (!taskId) return;
        const sinceId = reset ? 0 : (lateralState.lastEventId || 0);
        try {
            const meta = await loadTaskMeta(taskId);
            lateralState.taskMeta = meta;
        } catch (e) {
            lateralState.taskMeta = null;
        }
        try {
            const rows = await loadTaskEvents(taskId, sinceId, 12000);
            if (reset) {
                lateralState.events = rows;
            } else if (rows.length) {
                lateralState.events = (lateralState.events || []).concat(rows);
            }
            if (lateralState.events.length) {
                const last = lateralState.events[lateralState.events.length - 1];
                if (last && last.id) lateralState.lastEventId = last.id;
            }
            const classified = _classifyLateralSteps(lateralState.events);
            lateralState.steps = classified.steps;
            lateralState.tools = classified.tools;
            lateralState.artifacts = classified.artifacts;
            lateralState.info = classified.info;
            renderLateral();
        } catch (e) {}
    }

    function stopLateralTimer() {
        if (lateralState.timer) {
            clearInterval(lateralState.timer);
            lateralState.timer = null;
        }
    }

    function startLateralTimer() {
        stopLateralTimer();
        lateralState.timer = setInterval(() => {
            if (!lateralAutoRefresh || !lateralAutoRefresh.checked) return;
            if (!lateralState.taskId) return;
            loadLateralEvents(lateralState.taskId, false);
        }, 1500);
    }

    function initLateralMovePage() {
        if (lateralState.initialized) {
            startLateralTimer();
            loadLateralTasks().then(() => {});
            return;
        }
        lateralState.initialized = true;
        loadLateralTasks().then(() => {});
        renderLateral();

        if (lateralTaskSelect) {
            lateralTaskSelect.addEventListener('change', async () => {
                const taskId = String(lateralTaskSelect.value || '').trim();
                lateralState.taskId = taskId;
                lateralState.lastEventId = 0;
                lateralState.events = [];
                lateralState.steps = [];
                lateralState.tools = [];
                lateralState.artifacts = [];
                lateralState.info = {};
                lateralState.selectedStepId = 0;
                renderLateral();
                if (taskId) {
                    emitUiAudit('lateral_select_task', { task_id: taskId });
                    await loadLateralEvents(taskId, true);
                }
            });
        }
        if (lateralRefreshBtn) {
            lateralRefreshBtn.addEventListener('click', async () => {
                await loadLateralTasks();
                if (lateralState.taskId) await loadLateralEvents(lateralState.taskId, true);
            });
        }
        if (lateralAutoRefresh) {
            lateralAutoRefresh.addEventListener('change', () => {
                startLateralTimer();
            });
        }
        startLateralTimer();
    }

    function formatBytes(n) {
        const v = Number(n);
        if (!Number.isFinite(v) || v <= 0) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB'];
        let x = v;
        let u = 0;
        while (x >= 1024 && u < units.length - 1) {
            x /= 1024;
            u += 1;
        }
        return `${x.toFixed(u === 0 ? 0 : 1)} ${units[u]}`;
    }

    function _lootJoin(base, name) {
        const b = String(base || '').replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
        const n = String(name || '').replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
        if (!b) return n;
        if (!n) return b;
        return `${b}/${n}`;
    }

    function _lootParent(p) {
        const s = String(p || '').replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
        if (!s) return '';
        const parts = s.split('/').filter(Boolean);
        parts.pop();
        return parts.join('/');
    }

    function renderLootPath() {
        if (!lootPathBar) return;
        const p = String(lootState.path || '').replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
        if (!p) {
            lootPathBar.textContent = '/';
            return;
        }
        lootPathBar.textContent = `/${p}`;
    }

    function renderLootDetail(entry, previewText = null) {
        if (!lootDetailMeta || !lootDetailPath || !lootDetailSize || !lootDetailMtime || !lootDetailPreview) return;
        if (!entry) {
            lootDetailMeta.textContent = '—';
            lootDetailPath.textContent = '—';
            lootDetailSize.textContent = '—';
            lootDetailMtime.textContent = '—';
            lootDetailPreview.textContent = '选择一个文件以预览内容。';
            return;
        }
        const parts = [];
        parts.push(entry.is_dir ? '目录' : '文件');
        if (entry.name) parts.push(entry.name);
        lootDetailMeta.textContent = parts.join('  ·  ');
        lootDetailPath.textContent = entry.path || '';
        lootDetailSize.textContent = entry.is_dir ? '—' : formatBytes(entry.size || 0);
        lootDetailMtime.textContent = entry.mtime ? formatTs(entry.mtime) : '—';
        if (entry.is_dir) {
            lootDetailPreview.textContent = '目录不支持预览。';
        } else if (previewText !== null) {
            lootDetailPreview.textContent = String(previewText || '');
        } else {
            lootDetailPreview.textContent = '加载预览中...';
        }
    }

    function renderLootList() {
        if (!lootList) return;
        renderLootPath();
        lootList.innerHTML = '';
        const taskId = String(lootState.taskId || '').trim();
        if (!taskId) {
            lootList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-regular fa-folder-open" style="opacity: 0.5;"></i>
                    <p>请选择一个项目/任务</p>
                    <small style="display:block; margin-top:6px;">此处用于管理该项目已获取/留存的文件（上传/下载/预览）。</small>
                </div>
            `;
            renderLootDetail(null);
            return;
        }

        const rows = Array.isArray(lootState.entries) ? lootState.entries : [];
        if (!rows.length) {
            lootList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-regular fa-folder-open" style="opacity: 0.5;"></i>
                    <p>目录为空</p>
                </div>
            `;
            renderLootDetail(null);
            return;
        }

        const frag = document.createDocumentFragment();
        rows.forEach((e) => {
            const row = document.createElement('div');
            row.className = 'loot-row' + (lootState.selectedPath === e.path ? ' active' : '');
            row.dataset.path = e.path;

            const name = document.createElement('div');
            name.className = 'loot-cell';
            const icon = e.is_dir ? '<i class="fa-solid fa-folder" style="opacity:0.75;"></i>' : '<i class="fa-regular fa-file" style="opacity:0.75;"></i>';
            name.innerHTML = `${icon} <span style="margin-left:8px;">${e.name || ''}</span>`;

            const size = document.createElement('div');
            size.className = 'loot-cell small';
            size.textContent = e.is_dir ? '—' : formatBytes(e.size || 0);

            const mt = document.createElement('div');
            mt.className = 'loot-cell small';
            mt.textContent = e.mtime ? formatTs(e.mtime) : '';

            const actions = document.createElement('div');
            actions.className = 'loot-cell actions';
            const openBtn = document.createElement('button');
            openBtn.className = 'loot-mini-btn';
            openBtn.textContent = e.is_dir ? '打开' : '预览';
            const dlBtn = document.createElement('button');
            dlBtn.className = 'loot-mini-btn';
            dlBtn.textContent = '下载';
            const delBtn = document.createElement('button');
            delBtn.className = 'loot-mini-btn danger';
            delBtn.textContent = '删除';

            openBtn.addEventListener('click', (ev) => {
                ev.stopPropagation();
                if (e.is_dir) {
                    lootState.path = e.path;
                    lootState.selectedPath = '';
                    lootState.selectedEntry = null;
                    emitUiAudit('loot_enter_dir', { task_id: taskId, path: e.path });
                    loadLootList(true);
                } else {
                    selectLootEntry(e);
                }
            });
            dlBtn.addEventListener('click', (ev) => {
                ev.stopPropagation();
                emitUiAudit('loot_download', { task_id: taskId, path: e.path });
                window.open(`/api/loot/download?task_id=${encodeURIComponent(taskId)}&path=${encodeURIComponent(e.path)}`, '_blank');
            });
            delBtn.addEventListener('click', (ev) => {
                ev.stopPropagation();
                deleteLootEntry(e);
            });

            actions.appendChild(openBtn);
            actions.appendChild(dlBtn);
            actions.appendChild(delBtn);

            row.appendChild(name);
            row.appendChild(size);
            row.appendChild(mt);
            row.appendChild(actions);

            row.addEventListener('click', () => {
                if (e.is_dir) {
                    lootState.path = e.path;
                    lootState.selectedPath = '';
                    lootState.selectedEntry = null;
                    emitUiAudit('loot_enter_dir', { task_id: taskId, path: e.path });
                    loadLootList(true);
                    return;
                }
                selectLootEntry(e);
            });

            frag.appendChild(row);
        });
        lootList.appendChild(frag);
    }

    async function selectLootEntry(entry) {
        const taskId = String(lootState.taskId || '').trim();
        lootState.selectedPath = entry.path;
        lootState.selectedEntry = entry;
        renderLootList();
        renderLootDetail(entry, null);
        emitUiAudit('loot_preview', { task_id: taskId, path: entry.path });
        try {
            const res = await fetch(`/api/loot/read?task_id=${encodeURIComponent(taskId)}&path=${encodeURIComponent(entry.path)}&max_chars=50000`);
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                renderLootDetail(entry, data.error || '预览失败');
                return;
            }
            const hint = data.truncated ? '\n...[内容已截断]...' : '';
            renderLootDetail(entry, String(data.text || '') + hint);
        } catch (e) {
            renderLootDetail(entry, '预览失败');
        }
    }

    async function loadLootTasks() {
        if (!lootTaskSelect) return;
        try {
            const tasks = await fetchTasks(200);
            const current = lootTaskSelect.value;
            lootTaskSelect.innerHTML = '<option value=\"\">选择项目/任务...</option>';
            (tasks || []).forEach(t => {
                if (!t || !t.task_id) return;
                const opt = document.createElement('option');
                opt.value = String(t.task_id);
                const st = statusLabel(t.status);
                opt.textContent = `${t.task_id}  ·  ${st.text}`;
                lootTaskSelect.appendChild(opt);
            });
            if (current) lootTaskSelect.value = current;
        } catch (e) {}
    }

    async function loadLootRemoteSessions(taskId) {
        const tid = String(taskId || '').trim();
        lootState.remoteSessions = [];
        if (lootRemoteSessionSelect) {
            lootRemoteSessionSelect.innerHTML = '<option value=\"\">选择会话...</option>';
        }
        if (!tid) return;
        try {
            const res = await fetch(`/api/msf/sessions?task_id=${encodeURIComponent(tid)}`);
            const data = await res.json().catch(() => ({}));
            if (!res.ok) return;
            const sessions = Array.isArray(data.sessions) ? data.sessions : [];
            lootState.remoteSessions = sessions;
            if (lootRemoteSessionSelect) {
                lootRemoteSessionSelect.innerHTML = '<option value=\"\">选择会话...</option>';
                sessions.forEach(s => {
                    if (!s || !s.session_id) return;
                    const opt = document.createElement('option');
                    opt.value = String(s.session_id);
                    const k = s.kind ? String(s.kind) : '';
                    opt.textContent = k ? `#${s.session_id}  ·  ${k}` : `#${s.session_id}`;
                    lootRemoteSessionSelect.appendChild(opt);
                });
            }
            if (lootRemoteHint) {
                lootRemoteHint.textContent = sessions.length ? `已识别到 ${sessions.length} 个会话。` : '未识别到会话：可手动输入 session_id。';
            }
        } catch (e) {
            if (lootRemoteHint) lootRemoteHint.textContent = '会话加载失败：可手动输入 session_id。';
        }
    }

    function _getSelectedSessionId() {
        const a = lootRemoteSessionSelect ? String(lootRemoteSessionSelect.value || '').trim() : '';
        const b = lootRemoteSessionInput ? String(lootRemoteSessionInput.value || '').trim() : '';
        const v = a || b;
        const n = parseInt(v, 10);
        if (!Number.isFinite(n) || n <= 0) return 0;
        return n;
    }

    async function readRemoteFile() {
        const taskId = String(lootState.taskId || '').trim();
        if (!taskId) {
            alert('请先选择项目/任务');
            return;
        }
        const sid = _getSelectedSessionId();
        if (!sid) {
            alert('请选择或输入会话 ID');
            return;
        }
        const rp = lootRemotePathInput ? String(lootRemotePathInput.value || '').trim() : '';
        if (!rp) {
            alert('请输入远程文件路径');
            return;
        }
        lootState.lastRemote = null;
        renderLootDetail({ name: '远程读取', path: rp, is_dir: false, size: 0, mtime: 0 }, '读取中...');
        try {
            emitUiAudit('loot_remote_read', { task_id: taskId, session_id: sid, path: rp });
        } catch (e) {}
        try {
            const res = await fetch(`/api/msf/read_file?task_id=${encodeURIComponent(taskId)}&session_id=${encodeURIComponent(String(sid))}&path=${encodeURIComponent(rp)}&max_chars=50000`);
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                renderLootDetail({ name: '远程读取', path: rp, is_dir: false, size: 0, mtime: 0 }, data.error || '读取失败');
                return;
            }
            const text = String(data.text || '');
            lootState.lastRemote = { session_id: sid, path: rp, text: text };
            const hint = data.truncated ? '\n...[内容已截断]...' : '';
            renderLootDetail({ name: '远程读取', path: rp, is_dir: false, size: text.length, mtime: Date.now() / 1000 }, text + hint);
        } catch (e) {
            renderLootDetail({ name: '远程读取', path: rp, is_dir: false, size: 0, mtime: 0 }, '读取失败');
        }
    }

    async function saveRemoteToLoot() {
        const taskId = String(lootState.taskId || '').trim();
        if (!taskId) {
            alert('请先选择项目/任务');
            return;
        }
        const last = lootState.lastRemote;
        if (!last || !last.text) {
            alert('请先读取远程文件');
            return;
        }
        const rp = String(last.path || '').replace(/\\/g, '/');
        const base = rp.split('/').filter(Boolean).pop() || 'remote_file.txt';
        const blob = new Blob([last.text], { type: 'text/plain;charset=utf-8' });
        const file = new File([blob], base, { type: 'text/plain' });
        try {
            emitUiAudit('loot_remote_save', { task_id: taskId, session_id: last.session_id, remote_path: last.path, name: base, to_path: lootState.path || '' });
        } catch (e) {}
        await uploadLootFiles([file]);
    }

    async function loadLootList(resetSelection = false) {
        const taskId = String(lootState.taskId || (lootTaskSelect ? lootTaskSelect.value : '') || '').trim();
        lootState.taskId = taskId;
        if (!taskId) {
            lootState.entries = [];
            lootState.selectedPath = '';
            lootState.selectedEntry = null;
            renderLootList();
            return;
        }
        if (resetSelection) {
            lootState.selectedPath = '';
            lootState.selectedEntry = null;
            renderLootDetail(null);
        }
        const p = String(lootState.path || '').trim();
        try {
            const res = await fetch(`/api/loot/list?task_id=${encodeURIComponent(taskId)}&path=${encodeURIComponent(p)}`);
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                lootState.entries = [];
                renderLootList();
                return;
            }
            lootState.entries = Array.isArray(data.entries) ? data.entries : [];
            renderLootList();
        } catch (e) {
            lootState.entries = [];
            renderLootList();
        }
    }

    async function uploadLootFiles(fileList) {
        const taskId = String(lootState.taskId || '').trim();
        if (!taskId) {
            alert('请先选择项目/任务');
            return;
        }
        const files = Array.from(fileList || []);
        if (!files.length) return;
        const overwrite = Boolean(lootOverwriteToggle && lootOverwriteToggle.checked);
        const basePath = String(lootState.path || '').trim();

        for (const f of files.slice(0, 20)) {
            const fd = new FormData();
            fd.append('file', f, f.name);
            try {
                emitUiAudit('loot_upload', { task_id: taskId, path: basePath, name: f.name, size: f.size, overwrite: overwrite });
            } catch (e) {}
            try {
                const res = await fetch(`/api/loot/upload?task_id=${encodeURIComponent(taskId)}&path=${encodeURIComponent(basePath)}&overwrite=${overwrite ? 'true' : 'false'}`, {
                    method: 'POST',
                    body: fd,
                });
                const data = await res.json().catch(() => ({}));
                if (!res.ok) {
                    alert(data.error || '上传失败');
                    break;
                }
            } catch (e) {
                alert('上传失败');
                break;
            }
        }
        await loadLootList(true);
    }

    async function deleteLootEntry(entry) {
        const taskId = String(lootState.taskId || '').trim();
        if (!taskId) return;
        const ok = confirm(`确认删除：${entry.path} ？`);
        if (!ok) return;
        try {
            emitUiAudit('loot_delete', { task_id: taskId, path: entry.path });
        } catch (e) {}
        try {
            const res = await fetch(`/api/loot/delete?task_id=${encodeURIComponent(taskId)}&path=${encodeURIComponent(entry.path)}`, { method: 'DELETE' });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                alert(data.error || '删除失败');
                return;
            }
        } catch (e) {
            alert('删除失败');
            return;
        }
        if (lootState.selectedPath === entry.path) {
            lootState.selectedPath = '';
            lootState.selectedEntry = null;
            renderLootDetail(null);
        }
        await loadLootList(true);
    }

    async function mkdirLoot() {
        const taskId = String(lootState.taskId || '').trim();
        if (!taskId) {
            alert('请先选择项目/任务');
            return;
        }
        const name = prompt('请输入文件夹名称', '') || '';
        const folder = name.trim().replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
        if (!folder) return;
        const full = _lootJoin(String(lootState.path || ''), folder);
        try {
            emitUiAudit('loot_mkdir', { task_id: taskId, path: full });
        } catch (e) {}
        try {
            const res = await fetch('/api/loot/mkdir', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: taskId, path: full }),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                alert(data.error || '创建失败');
                return;
            }
        } catch (e) {
            alert('创建失败');
            return;
        }
        await loadLootList(true);
    }

    function stopLootTimer() {
        if (lootState.timer) {
            clearInterval(lootState.timer);
            lootState.timer = null;
        }
    }

    function startLootTimer() {
        stopLootTimer();
        lootState.timer = setInterval(() => {
            if (!lootAutoRefresh || !lootAutoRefresh.checked) return;
            if (!lootState.taskId) return;
            loadLootList(false);
        }, 5000);
    }

    function initLootPage() {
        if (lootState.initialized) {
            startLootTimer();
            loadLootTasks().then(() => {});
            return;
        }
        lootState.initialized = true;
        lootState.path = '';
        loadLootTasks().then(() => {});
        renderLootList();

        if (lootTaskSelect) {
            lootTaskSelect.addEventListener('change', async () => {
                const taskId = String(lootTaskSelect.value || '').trim();
                lootState.taskId = taskId;
                lootState.path = '';
                lootState.selectedPath = '';
                lootState.selectedEntry = null;
                lootState.lastRemote = null;
                renderLootList();
                if (taskId) {
                    emitUiAudit('loot_select_task', { task_id: taskId });
                }
                await loadLootRemoteSessions(taskId);
                await loadLootList(true);
            });
        }
        if (lootRefreshBtn) {
            lootRefreshBtn.addEventListener('click', async () => {
                await loadLootTasks();
                await loadLootList(false);
            });
        }
        if (lootAutoRefresh) {
            lootAutoRefresh.addEventListener('change', () => {
                startLootTimer();
            });
        }
        if (lootUpBtn) {
            lootUpBtn.addEventListener('click', () => {
                if (!lootState.taskId) return;
                const p = _lootParent(lootState.path);
                lootState.path = p;
                lootState.selectedPath = '';
                lootState.selectedEntry = null;
                emitUiAudit('loot_enter_dir', { task_id: lootState.taskId, path: p });
                loadLootList(true);
            });
        }
        if (lootRemoteReadBtn) lootRemoteReadBtn.addEventListener('click', () => readRemoteFile());
        if (lootRemoteSaveBtn) lootRemoteSaveBtn.addEventListener('click', () => saveRemoteToLoot());
        if (lootUploadBtn && lootUploadInput) {
            lootUploadBtn.addEventListener('click', () => {
                lootUploadInput.value = '';
                lootUploadInput.click();
            });
            lootUploadInput.addEventListener('change', async () => {
                await uploadLootFiles(lootUploadInput.files);
            });
        }
        if (lootMkdirBtn) lootMkdirBtn.addEventListener('click', () => mkdirLoot());
        if (lootDeleteBtn) lootDeleteBtn.addEventListener('click', async () => {
            if (!lootState.selectedEntry) {
                alert('请先选择一个文件');
                return;
            }
            await deleteLootEntry(lootState.selectedEntry);
        });
        if (lootDownloadBtn) lootDownloadBtn.addEventListener('click', () => {
            const taskId = String(lootState.taskId || '').trim();
            const e = lootState.selectedEntry;
            if (!taskId || !e || e.is_dir) {
                alert('请先选择一个文件');
                return;
            }
            emitUiAudit('loot_download', { task_id: taskId, path: e.path });
            window.open(`/api/loot/download?task_id=${encodeURIComponent(taskId)}&path=${encodeURIComponent(e.path)}`, '_blank');
        });
        if (lootPathBar) {
            lootPathBar.addEventListener('dblclick', () => {
                if (!lootState.taskId) return;
                const p = _lootParent(lootState.path);
                lootState.path = p;
                lootState.selectedPath = '';
                lootState.selectedEntry = null;
                emitUiAudit('loot_enter_dir', { task_id: lootState.taskId, path: p });
                loadLootList(true);
            });
        }
        startLootTimer();
    }
    
    // === Chat / Scan Logic ===
    if(startBtn) startBtn.addEventListener('click', startScan);
    if(stopBtn) stopBtn.addEventListener('click', stopScan);
    
    if(userInput) {
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !startBtn.disabled) {
                startScan();
            }
        });
    }

    // === Persist Task Logic ===
    // Check if task is running on load
    const savedTask = localStorage.getItem('currentTask');
    let startedFromRecovery = false;
    if (savedTask) {
        const { target, timestamp } = JSON.parse(savedTask);
        // Recover session if less than 24h old
        if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
            (async () => {
                try {
                    const res = await fetch(`/api/tasks/${encodeURIComponent(target)}`);
                    const status = await res.json();
                    if (status && status.task_id && (status.status === 'running' || status.status === 'paused')) {
                        userInput.value = target;
                        await startChatForTask(target, '', true);
                        startedFromRecovery = true;
                    } else {
                        localStorage.removeItem('currentTask');
                    }
                } catch (e) {
                    localStorage.removeItem('currentTask');
                }
            })();
        } else {
            localStorage.removeItem('currentTask');
        }
    }

    // Cross-browser/device recovery: if this browser has no local task, attach to the latest running task in TaskStore.
    if (!savedTask) {
        (async () => {
            try {
                const res = await fetch('/api/tasks?limit=10');
                const data = await res.json();
                const tasks = Array.isArray(data.tasks) ? data.tasks : [];
                const running = tasks.find(t => t && t.status === 'running' && t.task_id);
                if (!running || !running.task_id) return;

                const target = String(running.task_id);
                const st = await fetch(`/api/tasks/${encodeURIComponent(target)}`).then(r => r.json()).catch(() => null);
                if (!st || !st.task_id || st.status !== 'running') return;
                if (startedFromRecovery) return;

                userInput.value = target;
                await startChatForTask(target, '', true);
            } catch (e) {
                return;
            }
        })();
    }
    
    async function startScan(isRecovery = false) {
        const target = userInput.value.trim();
        if (!target) {
            alert('请输入目标 IP 或域名');
            return;
        }
        emitUiAudit('chat_submit_target', { task_id: target, source: isRecovery ? 'recovery' : 'manual' });
        await startChatForTask(target, '', isRecovery);
    }

    // Global retry state
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    let reconnectTimer = null;

    function connectSSE(url) {
        if (eventSource) {
            // Check readyState. If already connecting or open, do nothing?
            // Actually, if we call this, we usually want to force a new connection.
            // But if we are in a reconnect loop, we should be careful.
            eventSource.close();
        }
        
        // Reset retry count if this is a fresh manual start (not a retry call)
        // We can infer this if url is passed directly from startScan
        
        eventSource = new EventSource(url);
        
        eventSource.onopen = () => {
            console.log('SSE Connected');
            reconnectAttempts = 0; // Reset on success
            if(reconnectTimer) clearTimeout(reconnectTimer);
            // Hide any error messages?
        };
        
        eventSource.onmessage = (event) => {
            let data = null;
            try {
                data = JSON.parse(event.data);
            } catch (e) {
                return;
            }
            if (!data || data.type === 'ping') return;
            handleStreamEvent(data);
            
            // If task finished
            if (data.type === 'finish' || data.type === 'error') {
                 localStorage.removeItem('currentTask');
                 stopScan(true);
            }
        };
        
        eventSource.onerror = (error) => {
            console.error('SSE Error:', error);
            
            // Close current source to prevent browser's native rapid-fire retry
            eventSource.close();
            
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000); // Exponential backoff
                reconnectAttempts++;
                appendMessage('error', `连接断开。${timeout/1000}秒后尝试第 ${reconnectAttempts} 次重连...`);
                
                reconnectTimer = setTimeout(() => {
                    connectSSE(url);
                }, timeout);
            } else {
                appendMessage('error', '连接失败。任务可能仍在服务器运行，可刷新页面尝试重连，或点击停止结束任务。');
                stopBtn.style.display = 'inline-flex';
                stopBtn.disabled = false;
                userInput.disabled = true;
                userInput.placeholder = '连接已断开 (可刷新重连或停止任务)';
            }
        };
    }
    
    function stopScan(finished = false) {
        let targetToStop = null;
        try {
            const savedTask = localStorage.getItem('currentTask');
            if (savedTask) {
                targetToStop = JSON.parse(savedTask).target;
            }
        } catch (e) {}

        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectAttempts = 0;
        
        if (!finished) {
            if (targetToStop) {
                emitUiAudit('task_stop', { task_id: targetToStop, source: 'chat' });
                fetch(`/api/tasks/${encodeURIComponent(targetToStop)}/stop`, { method: 'POST' }).catch(() => {});
            }
            localStorage.removeItem('currentTask');
            appendMessage('system', '任务已手动停止');
        }
        
        startBtn.disabled = false;
        startBtn.style.display = 'inline-flex';
        stopBtn.style.display = 'none';
        
        // Unlock input
        userInput.disabled = false;
        userInput.value = ''; // Or keep target? Let's clear for new task.
        userInput.placeholder = '输入目标 IP 或域名 (例如: 192.168.1.1)';
        userInput.focus();
    }

    if (chatTaskSelect) {
        chatTaskSelect.addEventListener('change', async () => {
            const taskId = String(chatTaskSelect.value || '').trim();
            if (!taskId) return;
            try {
                await showTaskInChat(taskId);
            } catch (e) {
                appendMessage('error', `加载任务失败: ${e.message || e}`);
            }
        });
    }
    
    function handleStreamEvent(data) {
        // data structure: { type: 'log'|'thought'|'tool'|'result'|'error', content: '...' }
        
        if (data.type === 'log') {
            // Optional: log to console or a hidden debug panel
            console.log(`[LOG] ${data.content}`);
        } else if (data.type === 'thought') {
            appendMessage('ai', `**思考**: ${data.content}`);
        } else if (data.type === 'tool') {
            appendMessage('ai', `**执行工具**: \`${data.content}\``);
        } else if (data.type === 'result') {
            // Truncate long outputs for display
            let content = data.content;
            if (content.length > 2000) {
                content = content.substring(0, 2000) + "\n... (output truncated)";
            }
            appendMessage('ai', `**工具输出**:\n\`\`\`\n${content}\n\`\`\``);
        } else if (data.type === 'error') {
            appendMessage('error', `错误: ${data.content}`);
        } else if (data.type === 'report') {
            appendMessage('ai', `**报告已生成**: [查看报告](#)`);
            loadReports(); // Refresh report list
        } else if (data.type === 'vuln') {
            if (data.vuln && data.vuln.title) {
                appendMessage('ai', `**漏洞已登记**: ${data.vuln.severity || ''} - ${data.vuln.title}`);
            } else {
                appendMessage('ai', `**漏洞已登记**`);
            }
            loadVulnManager();
        }
        
        // Auto scroll
        // Only auto scroll if user is near bottom or if it's a new message
        const isNearBottom = chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight < 100;
        if (isNearBottom) {
             chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    function appendMessage(role, content) {
        const welcomeScreen = chatMessages.querySelector('.welcome-screen');
        if (welcomeScreen) {
            welcomeScreen.remove();
        }

        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${role}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        
        if (role === 'user') {
            avatarDiv.innerHTML = '<i class="fa-solid fa-user"></i>';
        } else if (role === 'ai') {
            avatarDiv.innerHTML = '<i class="fa-solid fa-robot"></i>';
        } else if (role === 'system') {
            avatarDiv.innerHTML = '<i class="fa-solid fa-circle-info"></i>';
        } else if (role === 'error') {
            avatarDiv.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
        }
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        // Use marked for content
        if (typeof marked !== 'undefined') {
             bubbleDiv.innerHTML = marked.parse(content);
        } else {
             bubbleDiv.textContent = content;
        }

        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(bubbleDiv);
        chatMessages.appendChild(msgDiv);
        
        // Ensure scroll to bottom on new message
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // === Reports Logic ===
    if(refreshReportsBtn) refreshReportsBtn.addEventListener('click', loadReports);
    if(refreshSkillsBtn) refreshSkillsBtn.addEventListener('click', loadSkills);
    if(refreshKnowledgeBtn) refreshKnowledgeBtn.addEventListener('click', loadKnowledge);
    if(refreshVulnsBtn) refreshVulnsBtn.addEventListener('click', loadVulnManager);
    if(vulnSeverityFilter) vulnSeverityFilter.addEventListener('change', loadVulnManager);
    if(vulnStatusFilter) vulnStatusFilter.addEventListener('change', loadVulnManager);
    if (vulnTaskSelect) vulnTaskSelect.addEventListener('change', async () => {
        const taskId = String(vulnTaskSelect.value || '').trim();
        vulnState.taskId = taskId;
        localStorage.setItem('vulnTaskId', taskId);
        await loadVulnManager();
    });
    if (vulnSearchInput) {
        let t = null;
        vulnSearchInput.addEventListener('input', () => {
            if (t) clearTimeout(t);
            t = setTimeout(() => loadVulnManager(), 250);
        });
    }
    if (exportVulnsBtn) exportVulnsBtn.addEventListener('click', () => exportVulnsForCurrentTask());
    
    async function loadReports() {
        if (!reportList) return;
        
        try {
            const res = await fetch('/api/reports');
            const data = await res.json();
            
            reportList.innerHTML = '';
            
            const reports = Array.isArray(data.reports) ? data.reports : [];
            if (reports.length > 0) {
                const groups = new Map();
                reports.forEach((report) => {
                    const ext = (report.split('.').pop() || '').toLowerCase();
                    const base = report.replace(/\.(md|txt|html|pdf)$/i, '');
                    if (!groups.has(base)) groups.set(base, { base, files: [], exts: new Set() });
                    groups.get(base).files.push(report);
                    groups.get(base).exts.add(ext);
                });

                const items = Array.from(groups.values()).sort((a, b) => (b.base || '').localeCompare(a.base || ''));

                items.forEach(g => {
                    const item = document.createElement('div');
                    item.className = 'report-card'; // We might need to style this
                    item.style.cssText = `
                        background: var(--bg-primary);
                        border: 1px solid var(--border-color);
                        border-radius: 8px;
                        padding: 16px;
                        margin-bottom: 12px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        transition: all 0.2s;
                    `;
                    
                    const iconClass = g.exts.has('html') ? 'fa-file-code' : 'fa-file-lines';
                    const preferView = g.exts.has('html') ? `${g.base}.html` : (g.exts.has('md') ? `${g.base}.md` : (g.exts.has('txt') ? `${g.base}.txt` : (g.files[0] || '')));
                    const filesAttr = encodeURIComponent(JSON.stringify(g.files || []));
                    const badges = ['md', 'html', 'pdf'].map(fmt => {
                        const ok = g.exts.has(fmt);
                        return `<span style="display:inline-flex; align-items:center; gap:6px; padding:2px 8px; border-radius:999px; border:1px solid var(--border-color); font-size:11px; color:${ok ? 'var(--text-primary)' : 'var(--text-secondary)'}; background:${ok ? 'rgba(0,0,0,0.03)' : 'transparent'};">${fmt.toUpperCase()}</span>`;
                    }).join('');
                    item.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <i class="fa-solid ${iconClass}" style="color: var(--accent-color); font-size: 1.5rem;"></i>
                            <div style="display:flex; flex-direction:column; gap:6px;">
                                <span style="font-weight: 600;">${g.base}</span>
                                <div style="display:flex; gap:6px; flex-wrap:wrap;">${badges}</div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button class="btn-small btn-primary view-report-btn" data-file="${preferView}" style="padding: 6px 12px; border-radius: 6px; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-secondary);">
                                <i class="fa-solid fa-eye"></i> 查看
                            </button>
                            <button class="btn-small btn-secondary download-report-btn" data-base="${g.base}" data-format="md" style="padding: 6px 10px; border-radius: 6px; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-secondary);">
                                <i class="fa-solid fa-download"></i> MD
                            </button>
                            <button class="btn-small btn-secondary download-report-btn" data-base="${g.base}" data-format="html" style="padding: 6px 10px; border-radius: 6px; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-secondary);">
                                <i class="fa-solid fa-download"></i> HTML
                            </button>
                            <button class="btn-small btn-secondary download-report-btn" data-base="${g.base}" data-format="pdf" style="padding: 6px 10px; border-radius: 6px; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-secondary);">
                                <i class="fa-solid fa-download"></i> PDF
                            </button>
                            <button class="btn-small btn-danger delete-report-btn" data-files="${filesAttr}" style="padding: 6px 12px; border-radius: 6px; cursor: pointer; border: 1px solid var(--error-color); background: #fff; color: var(--error-color);">
                                <i class="fa-solid fa-trash"></i> 删除
                            </button>
                        </div>
                    `;
                    reportList.appendChild(item);
                });
                
                // Add event listeners
                document.querySelectorAll('.view-report-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        viewReport(btn.dataset.file);
                    });
                });
                
                 document.querySelectorAll('.delete-report-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        let files = [];
                        const raw = String(btn.dataset.files || '').trim();
                        if (raw) {
                            try {
                                files = JSON.parse(decodeURIComponent(raw));
                            } catch (e) {
                                files = raw.split(',').map(s => s.trim()).filter(Boolean);
                            }
                        }
                        deleteReportGroup(files);
                    });
                });

                document.querySelectorAll('.download-report-btn').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        e.stopPropagation();
                        await downloadReport(btn.dataset.base, btn.dataset.format);
                    });
                });
                
            } else {
                reportList.innerHTML = `
                    <div class="empty-state" style="text-align: center; padding: 40px; color: var(--text-secondary);">
                        <i class="fa-regular fa-folder-open" style="font-size: 3rem; margin-bottom: 16px; opacity: 0.5;"></i>
                        <p>暂无报告文件</p>
                    </div>
                `;
            }
        } catch (err) {
            console.error('Load reports failed:', err);
        }
    }

    function _parseContentDispositionFilename(v) {
        const s = String(v || '');
        const m = /filename\*?=(?:UTF-8''|\"?)([^\";]+)/i.exec(s);
        if (!m) return '';
        try {
            return decodeURIComponent(m[1].replace(/\"/g, '').trim());
        } catch (e) {
            return m[1].replace(/\"/g, '').trim();
        }
    }

    async function downloadReport(base, format) {
        const b = (base || '').trim();
        const f = (format || '').trim().toLowerCase();
        if (!b || !f) return;
        try {
            const res = await fetch(`/api/reports/download?name=${encodeURIComponent(b)}&format=${encodeURIComponent(f)}`);
            if (!res.ok) {
                const msg = await res.text();
                alert('下载失败: ' + msg);
                return;
            }
            const blob = await res.blob();
            const cd = res.headers.get('content-disposition') || '';
            const fname = _parseContentDispositionFilename(cd) || `${b}.${f}`;
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fname;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1500);
        } catch (e) {
            alert('下载失败: ' + e.message);
        }
    }

    async function deleteReportGroup(files) {
        if (!Array.isArray(files) || files.length === 0) return;
        if (!confirm(`确定要删除该报告的所有格式文件吗？`)) return;
        const failed = [];
        for (const f of files) {
            const name = String(f || '').trim();
            if (!name) continue;
            try {
                const res = await fetch(`/api/reports/${encodeURIComponent(name)}`, { method: 'DELETE' });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    failed.push(`${name}: ${data.error || res.status}`);
                }
            } catch (e) {
                failed.push(`${name}: network_error`);
            }
        }
        if (failed.length) {
            alert('部分文件删除失败：\n' + failed.slice(0, 10).join('\n') + (failed.length > 10 ? `\n...(共 ${failed.length} 项)` : ''));
        }
        loadReports();
    }
    
    async function viewReport(filename) {
        try {
            emitUiAudit('report_view', { filename: filename });
            const ext = (filename.split('.').pop() || '').toLowerCase();
            if (ext === 'html') {
                window.open(`/files/reports/${encodeURIComponent(filename)}`, '_blank');
                return;
            }

            const res = await fetch(`/files/reports/${encodeURIComponent(filename)}`);
            if (!res.ok) throw new Error('Failed to fetch report');

            const text = await res.text();

            document.getElementById('reportModalTitle').textContent = filename;
            document.getElementById('reportModalBody').innerHTML = marked.parse(text);
            reportModal.style.display = 'block';
            
        } catch (err) {
            alert('无法加载报告: ' + err.message);
        }
    }
    
    async function deleteReport(filename) {
        if (!confirm(`确定要删除报告 ${filename} 吗？`)) return;
        
        try {
            emitUiAudit('report_delete', { filename: filename });
            const res = await fetch(`/api/reports/${encodeURIComponent(filename)}`, { method: 'DELETE' });
            if (res.ok) {
                loadReports();
            } else {
                const data = await res.json().catch(() => ({}));
                alert('删除失败: ' + (data.error || res.status));
            }
        } catch (err) {
            console.error(err);
            alert('删除出错');
        }
    }

    async function loadVulnManager() {
        if (!vulnList) return;
        const sev = (vulnSeverityFilter && vulnSeverityFilter.value) ? vulnSeverityFilter.value : '';
        const st = (vulnStatusFilter && vulnStatusFilter.value) ? vulnStatusFilter.value : '';
        const q = (vulnSearchInput && vulnSearchInput.value) ? String(vulnSearchInput.value || '').trim() : '';
        const taskId = String(vulnState.taskId || (vulnTaskSelect ? vulnTaskSelect.value : '') || '').trim();

        if (vulnTaskSelect && taskId && vulnTaskSelect.value !== taskId) {
            vulnTaskSelect.value = taskId;
        }
        if (!taskId) {
            if (vulnSummaryBar) vulnSummaryBar.textContent = '请选择项目/任务后查看对应漏洞。';
            vulnList.innerHTML = `
                <div class="empty-state" style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    <i class="fa-solid fa-folder-open" style="font-size: 3rem; margin-bottom: 16px; opacity: 0.4;"></i>
                    <p>请先选择一个项目/任务</p>
                    <small style="display:block; margin-top:6px;">选择后将仅展示该项目的漏洞记录</small>
                </div>
            `;
            return;
        }

        try {
            const res = await fetch(`/api/vulns?limit=500&task_id=${encodeURIComponent(taskId)}`);
            const data = await res.json();
            const vulns = Array.isArray(data.vulns) ? data.vulns : [];

            const filtered = vulns.filter(v => {
                if (sev && v.severity !== sev) return false;
                if (st && v.status !== st) return false;
                if (q) {
                    const hay = [
                        v.title || '',
                        v.target || '',
                        (v.details && v.details.affected) ? v.details.affected : '',
                        (v.details && v.details.evidence) ? v.details.evidence : '',
                    ].join(' ').toLowerCase();
                    if (!hay.includes(q.toLowerCase())) return false;
                }
                return true;
            });

            vulnList.innerHTML = '';
            vulnState.lastLoaded = filtered;

            if (vulnSummaryBar) {
                const total = vulns.length;
                const openCount = vulns.filter(x => x && x.status === 'open').length;
                const sevCnt = (level) => vulns.filter(x => x && x.severity === level).length;
                const parts = [
                    `任务：${taskId}`,
                    `总数：${total}`,
                    `未关闭：${openCount}`,
                    `严重：${sevCnt('严重')}`,
                    `高危：${sevCnt('高危')}`,
                    `中危：${sevCnt('中危')}`,
                    `低危：${sevCnt('低危')}`,
                ];
                if (q) parts.push(`搜索：${q}`);
                if (sev) parts.push(`等级：${sev}`);
                if (st) parts.push(`状态：${st}`);
                vulnSummaryBar.textContent = parts.join('  ·  ');
            }

            if (filtered.length === 0) {
                vulnList.innerHTML = `
                    <div class="empty-state" style="text-align: center; padding: 40px; color: var(--text-secondary);">
                        <i class="fa-solid fa-triangle-exclamation" style="font-size: 3rem; margin-bottom: 16px; opacity: 0.4;"></i>
                        <p>当前筛选条件下暂无漏洞</p>
                        <small style="display:block; margin-top:6px;">可尝试清空筛选，或切换项目/任务</small>
                    </div>
                `;
                return;
            }

            filtered.forEach(v => {
                const item = document.createElement('div');
                item.style.cssText = `
                    background: var(--bg-primary);
                    border: 1px solid var(--border-color);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: 14px;
                `;

                const sevColor = v.severity === '严重' ? 'var(--error-color)'
                    : v.severity === '高危' ? '#ff6b35'
                    : v.severity === '中危' ? 'var(--warning-color)'
                    : 'var(--text-secondary)';

                const affected = (v.details && v.details.affected) ? v.details.affected : '';
                const cvss = (v.cvss !== null && v.cvss !== undefined) ? Number(v.cvss).toFixed(1) : '';
                const meta = [
                    v.target ? `目标: ${v.target}` : '',
                    v.task_id ? `任务: ${v.task_id}` : '',
                    affected ? `影响点: ${affected}` : '',
                    cvss ? `CVSS: ${cvss}` : '',
                    v.status ? `状态: ${v.status}` : ''
                ].filter(Boolean).join(' | ');

                item.innerHTML = `
                    <div style="min-width:0;">
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                            <span style="display:inline-flex; align-items:center; gap:6px; padding:4px 10px; border-radius: 999px; background: rgba(0,0,0,0.04); border: 1px solid var(--border-color); font-size: 12px; color: ${sevColor}; font-weight: 600;">
                                <i class="fa-solid fa-circle-exclamation"></i> ${v.severity || '中危'}
                            </span>
                            <span style="font-weight: 600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${v.title || '(未命名漏洞)'}</span>
                        </div>
                        <div style="color: var(--text-secondary); font-size: 12px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${meta}</div>
                    </div>
                    <div style="display:flex; gap:8px; flex-shrink:0;">
                        <button class="btn-small btn-primary view-vuln-btn" data-id="${v.vuln_id}" style="padding: 6px 12px; border-radius: 6px; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-secondary);">
                            <i class="fa-solid fa-eye"></i> 查看
                        </button>
                        <button class="btn-small btn-danger delete-vuln-btn" data-id="${v.vuln_id}" style="padding: 6px 12px; border-radius: 6px; cursor: pointer; border: 1px solid var(--error-color); background: #fff; color: var(--error-color);">
                            <i class="fa-solid fa-trash"></i> 删除
                        </button>
                    </div>
                `;
                vulnList.appendChild(item);
            });

            document.querySelectorAll('.view-vuln-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    viewVuln(btn.dataset.id);
                });
            });
            document.querySelectorAll('.delete-vuln-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    deleteVuln(btn.dataset.id);
                });
            });
        } catch (e) {
            console.error(e);
        }
    }

    function exportVulnsForCurrentTask() {
        const taskId = String(vulnState.taskId || '').trim();
        if (!taskId) {
            alert('请先选择项目/任务');
            return;
        }
        const rows = Array.isArray(vulnState.lastLoaded) ? vulnState.lastLoaded : [];
        const ts = new Date().toISOString().replace(/[:.]/g, '-');
        const mdLines = [];
        mdLines.push(`# 漏洞清单（${taskId}）`);
        mdLines.push('');
        mdLines.push(`导出时间：${new Date().toLocaleString()}`);
        mdLines.push('');
        if (!rows.length) {
            mdLines.push('暂无漏洞。');
        } else {
            rows.forEach((v, idx) => {
                const d = v.details || {};
                mdLines.push(`## ${idx + 1}. ${v.title || '(未命名漏洞)'}`);
                mdLines.push('');
                mdLines.push(`- 等级：${v.severity || ''}${(v.cvss !== null && v.cvss !== undefined) ? `（CVSS ${Number(v.cvss).toFixed(1)}）` : ''}`);
                mdLines.push(`- 状态：${v.status || 'open'}`);
                mdLines.push(`- 目标：${v.target || ''}`);
                mdLines.push(`- 任务：${v.task_id || ''}`);
                if (d.affected) mdLines.push(`- 影响点：${d.affected}`);
                mdLines.push('');
                if (d.evidence) {
                    mdLines.push('**证据摘要**');
                    mdLines.push('');
                    mdLines.push(String(d.evidence));
                    mdLines.push('');
                }
                if (d.remediation) {
                    mdLines.push('**修复建议**');
                    mdLines.push('');
                    mdLines.push(String(d.remediation));
                    mdLines.push('');
                }
            });
        }
        const blob = new Blob([mdLines.join('\n')], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `vulns_${taskId}_${ts}.md`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        emitUiAudit('export_vulns', { task_id: taskId, count: rows.length });
    }

    function stopMsfCliUiTimer() {
        if (msfCliUiState.timer) {
            clearInterval(msfCliUiState.timer);
            msfCliUiState.timer = null;
        }
    }

    async function loadMsfSessionsIntoSelect(taskId, selectEl) {
        if (!selectEl) return;
        selectEl.innerHTML = '<option value=\"\">选择会话（可选）...</option>';
        const tid = String(taskId || '').trim();
        if (!tid) return;
        try {
            const res = await fetch(`/api/msf/sessions?task_id=${encodeURIComponent(tid)}`);
            const data = await res.json().catch(() => ({}));
            if (!res.ok) return;
            const sessions = Array.isArray(data.sessions) ? data.sessions : [];
            sessions.forEach(s => {
                if (!s || !s.session_id) return;
                const opt = document.createElement('option');
                opt.value = String(s.session_id);
                opt.textContent = `#${s.session_id}` + (s.kind ? `  ·  ${s.kind}` : '');
                selectEl.appendChild(opt);
            });
            if (sessions.length) {
                selectEl.value = String(sessions[sessions.length - 1].session_id);
            }
        } catch (e) {}
    }

    function appendMsfCliOutput(pre, lines) {
        if (!pre || !Array.isArray(lines) || !lines.length) return;
        const text = lines.map(x => String(x.line || '')).join('');
        pre.textContent = (pre.textContent || '') + text;
        pre.scrollTop = pre.scrollHeight;
    }

    async function pollMsfCliOnce(panelTaskId) {
        const tid = String(panelTaskId || '').trim();
        if (!tid) return;
        const statusEl = document.getElementById('msfCliStatusText');
        const outEl = document.getElementById('msfCliOutput');
        try {
            const stRes = await fetch(`/api/msf/cli/status?task_id=${encodeURIComponent(tid)}`);
            const st = await stRes.json().catch(() => ({}));
            const running = Boolean(st.running);
            const pid = st.pid ? String(st.pid) : '';
            if (statusEl) statusEl.textContent = running ? `MSF 进程运行中${pid ? `  ·  PID ${pid}` : ''}` : 'MSF 未运行：只有“利用成功且连接仍在保留”时才可手动接管';
        } catch (e) {
            if (statusEl) statusEl.textContent = '状态获取失败';
        }

        try {
            const res = await fetch(`/api/msf/cli/output?task_id=${encodeURIComponent(tid)}&since=${encodeURIComponent(String(msfCliUiState.seq || 0))}&limit=800`);
            const data = await res.json().catch(() => ({}));
            if (!res.ok) return;
            msfCliUiState.seq = Number(data.seq || msfCliUiState.seq || 0);
            appendMsfCliOutput(outEl, Array.isArray(data.lines) ? data.lines : []);
        } catch (e) {}
    }

    async function sendMsfCliCmd(taskId, cmd) {
        const tid = String(taskId || '').trim();
        const c = String(cmd || '').trim();
        if (!tid || !c) return;
        try {
            emitUiAudit('msf_cli_send', { task_id: tid, cmd_len: c.length });
        } catch (e) {}
        try {
            const res = await fetch('/api/msf/cli/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: tid, cmd: c }),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                alert(data.error || '发送失败');
            }
        } catch (e) {
            alert('发送失败');
        }
        await pollMsfCliOnce(tid);
    }

    async function stopMsfCli(taskId) {
        const tid = String(taskId || '').trim();
        if (!tid) return;
        const ok = confirm('确认断开并停止后台 MSF 进程？');
        if (!ok) return;
        try {
            emitUiAudit('msf_cli_stop', { task_id: tid });
        } catch (e) {}
        try {
            const res = await fetch('/api/msf/cli/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: tid }),
            });
            await res.json().catch(() => ({}));
        } catch (e) {}
        await pollMsfCliOnce(tid);
    }

    async function initMsfCliPanel(taskId, vulnId) {
        stopMsfCliUiTimer();
        msfCliUiState.taskId = String(taskId || '').trim();
        msfCliUiState.vulnId = String(vulnId || '').trim();
        msfCliUiState.seq = 0;

        const tid = msfCliUiState.taskId;
        const sessionSelect = document.getElementById('msfCliSessionSelect');
        const input = document.getElementById('msfCliInput');
        const sendBtn = document.getElementById('msfCliSendBtn');
        const refreshBtn = document.getElementById('msfCliRefreshBtn');
        const stopBtn = document.getElementById('msfCliStopBtn');
        const sessionsBtn = document.getElementById('msfCliSessionsBtn');
        const whoamiBtn = document.getElementById('msfCliWhoamiBtn');
        const getuidBtn = document.getElementById('msfCliGetuidBtn');
        const outEl = document.getElementById('msfCliOutput');
        if (outEl) outEl.textContent = '';

        await loadMsfSessionsIntoSelect(tid, sessionSelect);
        await pollMsfCliOnce(tid);

        const getSid = () => {
            const v = sessionSelect ? String(sessionSelect.value || '').trim() : '';
            const n = parseInt(v, 10);
            if (!Number.isFinite(n) || n <= 0) return 0;
            return n;
        };

        if (refreshBtn) refreshBtn.onclick = () => pollMsfCliOnce(tid);
        if (stopBtn) stopBtn.onclick = () => stopMsfCli(tid);
        if (sendBtn) sendBtn.onclick = () => {
            const c = input ? String(input.value || '') : '';
            if (input) input.value = '';
            sendMsfCliCmd(tid, c);
        };
        if (input) {
            input.onkeydown = (e) => {
                if (e.key === 'Enter') {
                    const c = String(input.value || '');
                    input.value = '';
                    sendMsfCliCmd(tid, c);
                }
            };
        }
        if (sessionsBtn) sessionsBtn.onclick = () => sendMsfCliCmd(tid, 'sessions -l');
        if (whoamiBtn) whoamiBtn.onclick = () => {
            const sid = getSid();
            if (!sid) return sendMsfCliCmd(tid, 'sessions -l');
            return sendMsfCliCmd(tid, `sessions -i ${sid} -C "whoami"`);
        };
        if (getuidBtn) getuidBtn.onclick = () => {
            const sid = getSid();
            if (!sid) return sendMsfCliCmd(tid, 'sessions -l');
            return sendMsfCliCmd(tid, `sessions -i ${sid} -C "getuid"`);
        };

        msfCliUiState.timer = setInterval(() => {
            if (!vulnModal || vulnModal.style.display !== 'block') return;
            pollMsfCliOnce(tid);
        }, 1200);
    }

    async function viewVuln(vulnId) {
        try {
            emitUiAudit('vuln_view', { vuln_id: vulnId, task_id: vulnState.taskId || '' });
            const res = await fetch(`/api/vulns/${encodeURIComponent(vulnId)}`);
            if (!res.ok) throw new Error('Failed to fetch vuln');
            const v = await res.json();
            if (vulnModalTitle) vulnModalTitle.textContent = `${v.severity || ''} - ${v.title || '漏洞详情'}`;

            const d = v.details || {};
            const md = `# ${v.title || '漏洞详情'}

**等级**：${v.severity || ''}  ${v.cvss !== null && v.cvss !== undefined ? `（CVSS: ${Number(v.cvss).toFixed(1)}）` : ''}

**目标**：${v.target || ''}  
**任务**：${v.task_id || ''}  
**状态**：${v.status || 'open'}

## 受影响点
${d.affected || '未提供'}

## 漏洞原理
${d.principle || '未提供'}

## 影响与危害
${d.impact || '未提供'}

## 证据摘要
${d.evidence || '未提供'}

## 修复建议
${d.remediation || '未提供'}

## 参考资料
${d.references || '无'}
`;
            if (vulnModalBody) {
                const html = (typeof marked !== 'undefined') ? marked.parse(md) : md;
                vulnModalBody.innerHTML = html + `
                    <hr style="margin: 18px 0; border: none; border-top: 1px solid var(--border-color);" />
                    <div class="msf-cli-panel" id="msfCliPanel">
                        <div class="msf-cli-head">
                            <div class="msf-cli-title">交互式 CLI（保留连接）</div>
                            <div class="msf-cli-actions">
                                <button class="btn-secondary" id="msfCliRefreshBtn"><i class="fa-solid fa-rotate-right"></i> 刷新</button>
                                <button class="btn-danger" id="msfCliStopBtn"><i class="fa-solid fa-stop"></i> 断开</button>
                            </div>
                        </div>
                        <div class="msf-cli-meta" id="msfCliStatusText">加载中...</div>
                        <div class="msf-cli-row">
                            <select id="msfCliSessionSelect" class="audit-input" style="min-width: 220px;">
                                <option value="">选择会话（可选）...</option>
                            </select>
                            <button class="btn-secondary" id="msfCliSessionsBtn">sessions -l</button>
                            <button class="btn-secondary" id="msfCliWhoamiBtn">whoami</button>
                            <button class="btn-secondary" id="msfCliGetuidBtn">getuid</button>
                        </div>
                        <pre class="msf-cli-output" id="msfCliOutput"></pre>
                        <div class="msf-cli-input-row">
                            <input id="msfCliInput" class="audit-input" style="flex: 1; min-width: 280px;" placeholder="输入 MSF 命令（例如 sessions -i 1）">
                            <button class="btn-primary" id="msfCliSendBtn"><i class="fa-solid fa-paper-plane"></i> 发送</button>
                        </div>
                        <div class="msf-cli-hint">提示：只有在“漏洞利用成功（打开会话）且后台 MSF 进程仍在运行”时，才可继续操作会话。</div>
                    </div>
                `;
            }
            if (vulnModal) vulnModal.style.display = 'block';
            initMsfCliPanel(v.task_id || vulnState.taskId || '', vulnId);
        } catch (e) {
            alert('无法加载漏洞详情: ' + e.message);
        }
    }

    async function deleteVuln(vulnId) {
        if (!confirm('确定要删除该漏洞记录吗？')) return;
        try {
            emitUiAudit('vuln_delete', { vuln_id: vulnId, task_id: vulnState.taskId || '' });
            const res = await fetch(`/api/vulns/${encodeURIComponent(vulnId)}`, { method: 'DELETE' });
            if (res.ok) {
                loadVulnManager();
            } else {
                alert('删除失败');
            }
        } catch (e) {
            alert('删除出错: ' + e.message);
        }
    }

    if (closeVulnModal && vulnModal) {
        closeVulnModal.addEventListener('click', () => {
            vulnModal.style.display = 'none';
            stopMsfCliUiTimer();
        });
    }
    
    // Modal Logic
    if(closeModal) {
        closeModal.addEventListener('click', () => {
            reportModal.style.display = 'none';
        });
    }
    
    window.addEventListener('click', (e) => {
        if (e.target === reportModal) {
            reportModal.style.display = 'none';
        }
        if (vulnModal && e.target === vulnModal) {
            vulnModal.style.display = 'none';
            stopMsfCliUiTimer();
        }
    });
    
    // === Tools Logic ===
    async function loadTools() {
        if (!toolsList) return;
        
        try {
            const res = await fetch('/api/tools');
            const data = await res.json();
            const count = Array.isArray(data.tools) ? data.tools.length : 0;
            if (toolsCountBadge) toolsCountBadge.textContent = String(count);
            
            toolsList.innerHTML = '';
            // Set grid style for toolsList
            toolsList.style.cssText = `
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 20px;
            `;
            
            if (data.tools) {
                data.tools.forEach(tool => {
                    const card = document.createElement('div');
                    card.style.cssText = `
                        background: var(--bg-primary);
                        border: 1px solid var(--border-color);
                        border-radius: 12px;
                        padding: 20px;
                        transition: all 0.2s;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                    `;
                    // Determine description to display: prefer short_description, fallback to first line/paragraph of description
                    let displayDesc = tool.short_description;
                    if (!displayDesc && tool.description) {
                        // Split by double newline to get first paragraph, or just first line if single newline
                        const parts = tool.description.split('\n');
                        // Find first non-empty line
                        for (let line of parts) {
                            if (line.trim()) {
                                displayDesc = line.trim();
                                break;
                            }
                        }
                    }

                    card.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                            <div style="width: 32px; height: 32px; background: rgba(0, 102, 255, 0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: var(--accent-color);">
                                <i class="fa-solid fa-terminal"></i>
                            </div>
                            <div style="display:flex; flex-direction:column; gap:4px; min-width:0;">
                                <h3 style="margin: 0; font-size: 1.1rem; font-weight: 600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${tool.name}</h3>
                                <div style="display:flex; gap:6px; align-items:center;">
                                    <span style="display:inline-flex; align-items:center; gap:6px; padding:3px 8px; border-radius:999px; border:1px solid var(--border-color); font-size:11px; color:${tool.agent_allowed ? '#28a745' : 'var(--text-secondary)'}; background:${tool.agent_allowed ? 'rgba(40,167,69,0.08)' : 'rgba(0,0,0,0.03)'};">
                                        <i class="fa-solid ${tool.agent_allowed ? 'fa-circle-check' : 'fa-circle-minus'}"></i>
                                        ${tool.agent_allowed ? '可自动调度' : '仅手动/展示'}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; flex: 1;">${displayDesc || '无描述'}</p>
                    `;
                    toolsList.appendChild(card);
                });
            }
        } catch (err) {
            console.error('Load tools failed:', err);
        }
    }
    
    // === Skills Logic ===
    async function loadSkills() {
        if (!skillsList) return;
        try {
            const res = await fetch('/api/skills');
            const data = await res.json();
            skillsList.innerHTML = '';
            const count = Array.isArray(data.skills) ? data.skills.length : 0;
            if (skillsCountBadge) skillsCountBadge.textContent = String(count);
            
            if (data.skills && data.skills.length > 0) {
                data.skills.forEach(skill => {
                    const item = document.createElement('div');
                    item.className = 'task-item report-item'; // Use report-item for hover effect
                    item.innerHTML = `
                        <div class="task-header">
                            <div class="task-info">
                                <i class="fa-solid fa-brain" style="color: var(--accent-color); font-size: 1.2rem;"></i>
                                <span class="task-message">${skill.name}</span>
                            </div>
                            <div class="task-actions">
                                <button class="btn-small btn-primary view-skill-btn" data-file="${skill.name}" data-type="skills">
                                    <i class="fa-solid fa-eye"></i> 查看
                                </button>
                            </div>
                        </div>
                    `;
                    skillsList.appendChild(item);
                });
                
                // Add event listeners
                document.querySelectorAll('.view-skill-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        viewContent(btn.dataset.type, btn.dataset.file);
                    });
                });
            } else {
                skillsList.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-brain" style="opacity: 0.5;"></i>
                        <p>暂无 Skill 文件</p>
                    </div>
                `;
            }
        } catch (err) {
            console.error('Load skills failed:', err);
        }
    }

    // === Knowledge Logic ===
    async function loadKnowledge() {
        if (!knowledgeList) return;
        try {
            const res = await fetch('/api/knowledge');
            const data = await res.json();
            knowledgeList.innerHTML = '';
            const count = Array.isArray(data.knowledge) ? data.knowledge.length : 0;
            if (knowledgeCountBadge) knowledgeCountBadge.textContent = String(count);
            
            if (data.knowledge && data.knowledge.length > 0) {
                data.knowledge.forEach(item => {
                    const el = document.createElement('div');
                    el.className = 'task-item report-item';
                    el.innerHTML = `
                        <div class="task-header">
                            <div class="task-info">
                                <i class="fa-solid fa-book" style="color: var(--success-color); font-size: 1.2rem;"></i>
                                <span class="task-message">${item.name}</span>
                            </div>
                            <div class="task-actions">
                                <button class="btn-small btn-primary view-knowledge-btn" data-file="${item.name}" data-type="knowledge">
                                    <i class="fa-solid fa-eye"></i> 查看
                                </button>
                            </div>
                        </div>
                    `;
                    knowledgeList.appendChild(el);
                });
                
                document.querySelectorAll('.view-knowledge-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        viewContent(btn.dataset.type, btn.dataset.file);
                    });
                });
            } else {
                knowledgeList.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-book" style="opacity: 0.5;"></i>
                        <p>暂无知识库文件</p>
                    </div>
                `;
            }
        } catch (err) {
            console.error('Load knowledge failed:', err);
        }
    }

    // === Vulnerability DB Logic ===
    const searchVulnBtn = document.getElementById('searchVulnBtn');
    const vulndbSearchInput = document.getElementById('vulndbSearchInput');
    
    if (searchVulnBtn) {
        searchVulnBtn.addEventListener('click', () => {
            const query = vulndbSearchInput.value.trim();
            if (!query) {
                renderVulnDbEmptyPrompt();
                return;
            }
            loadVulnerabilities(query);
        });
    }
    
    if (vulndbSearchInput) {
        vulndbSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = vulndbSearchInput.value.trim();
                if (!query) {
                    renderVulnDbEmptyPrompt();
                    return;
                }
                loadVulnerabilities(query);
            }
        });
        vulndbSearchInput.addEventListener('input', () => {
            const q = vulndbSearchInput.value.trim();
            if (!q) {
                renderVulnDbEmptyPrompt();
            }
        });
    }

    function renderVulnDbEmptyPrompt() {
        if (!vulndbList) return;
        vulndbList.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-shield-cat" style="opacity: 0.5; font-size: 3rem; margin-bottom: 16px;"></i>
                <p>请输入关键词搜索 Exploit-DB</p>
                <small style="display:block; margin-top:6px;">示例：CVE-2021-44228 / Apache 2.4.49 / ThinkPHP</small>
                <div style="margin-top:14px; display:flex; gap:10px; justify-content:center; flex-wrap:wrap;">
                    <button class="btn-secondary" id="loadLocalVulnNotesBtn" style="padding: 8px 12px;">
                        <i class="fa-solid fa-folder-open"></i> 加载本地漏洞笔记
                    </button>
                </div>
                <small style="display:block; margin-top:10px; color: var(--text-secondary);">
                    本地漏洞笔记用于展示你导入/沉淀的资料，不代表 Exploit-DB 全量。
                </small>
            </div>
        `;
        const btn = document.getElementById('loadLocalVulnNotesBtn');
        if (btn) {
            btn.addEventListener('click', () => {
                loadLocalVulnNotes();
            });
        }
    }

    async function loadLocalVulnNotes() {
        if (!vulndbList) return;
        vulndbList.innerHTML = '<div style="text-align:center; padding: 20px;"><i class="fa-solid fa-spinner fa-spin"></i> 正在加载本地漏洞笔记...</div>';
        try {
            const res = await fetch('/api/vulndb');
            const data = await res.json();
            const items = Array.isArray(data.vulndb) ? data.vulndb : [];
            vulndbList.innerHTML = '';

            if (items.length > 0) {
                items.forEach(item => {
                    const el = document.createElement('div');
                    el.className = 'task-item report-item';
                    el.innerHTML = `
                        <div class="task-header">
                            <div class="task-info">
                                <i class="fa-solid fa-bug" style="color: var(--error-color); font-size: 1.2rem;"></i>
                                <div style="display:flex; flex-direction:column;">
                                    <span class="task-message" style="font-weight:600;">${item.name}</span>
                                    <span style="font-size:0.8rem; color:var(--text-secondary);">本地漏洞笔记</span>
                                </div>
                            </div>
                            <div class="task-actions">
                                <button class="btn-small btn-primary view-vulndb-btn" data-file="${item.name}" style="padding: 6px 12px; border-radius: 6px; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-secondary);">
                                    <i class="fa-solid fa-eye"></i> 查看
                                </button>
                            </div>
                        </div>
                    `;
                    vulndbList.appendChild(el);
                });
                document.querySelectorAll('.view-vulndb-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        viewContent('vulndb', btn.dataset.file);
                    });
                });
            } else {
                vulndbList.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-shield-cat" style="opacity: 0.5; font-size: 3rem; margin-bottom: 16px;"></i>
                        <p>本地漏洞笔记为空</p>
                        <small style="display:block; margin-top:6px;">请使用上方搜索框检索 Exploit-DB，或导入/沉淀资料到 data/vulndb。</small>
                    </div>
                `;
            }
        } catch (err) {
            console.error('Load vulndb failed:', err);
            vulndbList.innerHTML = `<div class="empty-state"><p style="color:var(--error-color);">加载失败: ${err.message}</p></div>`;
        }
    }

    async function loadVulnerabilities(query = '') {
        if (!vulndbList) return;

        if (!query) {
            renderVulnDbEmptyPrompt();
            return;
        }

        vulndbList.innerHTML = '<div style="text-align:center; padding: 20px;"><i class="fa-solid fa-spinner fa-spin"></i> 正在搜索 Exploit-DB...</div>';

        try {
            const url = query ? `/api/vulnerabilities?query=${encodeURIComponent(query)}` : '/api/vulnerabilities';
            const res = await fetch(url);
            const data = await res.json();
            vulndbList.innerHTML = '';
            
            if (data.vulnerabilities && data.vulnerabilities.length > 0) {
                data.vulnerabilities.forEach(item => {
                    const el = document.createElement('div');
                    el.className = 'task-item report-item';
                    
                    // Handle searchsploit result structure or fallback file structure
                    const title = item.Title || item.name;
                    const id = item.EDB_ID || item.name;
                    const type = item.Type || 'exploit';
                    const platform = item.Platform || '';
                    
                    el.innerHTML = `
                        <div class="task-header">
                            <div class="task-info">
                                <i class="fa-solid fa-bug" style="color: var(--error-color); font-size: 1.2rem;"></i>
                                <div style="display:flex; flex-direction:column;">
                                    <span class="task-message" style="font-weight:600;">${title}</span>
                                    <span style="font-size:0.8rem; color:var(--text-secondary);">
                                        EDB-ID: ${id} | Type: ${type} ${platform ? '| Platform: ' + platform : ''}
                                    </span>
                                </div>
                            </div>
                             <div class="task-actions">
                                <!-- Future: View Details for EDB items -->
                            </div>
                        </div>
                    `;
                    vulndbList.appendChild(el);
                });
            } else {
                vulndbList.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-shield-cat" style="opacity: 0.5; font-size: 3rem; margin-bottom: 16px;"></i>
                        <p>${query ? '未找到相关 Exploit' : '请输入关键词搜索 Exploit-DB'}</p>
                        ${data.error ? `<p style="color:var(--error-color); font-size:0.9rem; margin-top:8px;">${data.error}</p>` : ''}
                    </div>
                `;
            }
        } catch (err) {
            console.error('Load vulndb failed:', err);
            vulndbList.innerHTML = `<div class="empty-state"><p style="color:var(--error-color);">加载失败: ${err.message}</p></div>`;
        }
    }

    async function loadVulnDbStats() {
        try {
            const res = await fetch('/api/vulnerabilities/stats');
            const data = await res.json();
            const ok = Boolean(data && data.exploitdb_available);
            const total = ok ? Number(data.exploitdb_total) : null;
            const text = (total !== null && Number.isFinite(total)) ? total.toLocaleString() : '--';
            if (vulnDbTotalCountBadge) vulnDbTotalCountBadge.textContent = text;
        } catch (e) {
            if (vulnDbTotalCountBadge) vulnDbTotalCountBadge.textContent = '--';
        }
    }

    async function loadHealth() {
        if (!healthBadge) return;
        try {
            const res = await fetch('/api/health');
            const h = await res.json();
            const warnings = Array.isArray(h.warnings) ? h.warnings : [];
            const ok = Boolean(h.ok);

            healthBadge.classList.remove('status-success', 'status-warning', 'status-danger');

            if (ok && warnings.length === 0) {
                healthBadge.classList.add('status-success');
                healthBadge.innerHTML = '<i class="fa-solid fa-circle-check"></i> 系统就绪';
                healthBadge.title = '';
            } else if (ok) {
                healthBadge.classList.add('status-warning');
                healthBadge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> 部分功能降级';
                healthBadge.title = warnings.join('\n');
            } else {
                healthBadge.classList.add('status-danger');
                healthBadge.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> 需要配置';
                healthBadge.title = warnings.join('\n');
            }
        } catch (e) {
            healthBadge.classList.remove('status-success', 'status-warning');
            healthBadge.classList.add('status-danger');
            healthBadge.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> 健康检查失败';
        }
    }

    function formatBytesPerSec(n) {
        const v = Number(n);
        if (!Number.isFinite(v) || v <= 0) return '0 B/s';
        const units = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
        let x = v;
        let u = 0;
        while (x >= 1024 && u < units.length - 1) {
            x /= 1024;
            u += 1;
        }
        return `${x.toFixed(u === 0 ? 0 : 1)} ${units[u]}`;
    }

    let lastDiskIo = null;
    let lastDiskIoTs = null;

    async function pollPerf() {
        if (!perfMonitor) return;
        try {
            const res = await fetch('/api/system/metrics');
            const m = await res.json();
            if (!m || m.available === false) {
                if (perfCpu) perfCpu.textContent = 'N/A';
                if (perfMem) perfMem.textContent = 'N/A';
                if (perfDisk) perfDisk.textContent = '--%';
                if (perfDiskIo) perfDiskIo.textContent = 'psutil 未安装';
                return;
            }

            if (perfCpu) perfCpu.textContent = (m.cpu_percent !== null && m.cpu_percent !== undefined) ? `${Number(m.cpu_percent).toFixed(0)}%` : 'N/A';
            if (perfMem) {
                const mp = m.memory && m.memory.percent !== undefined ? Number(m.memory.percent) : null;
                perfMem.textContent = (mp !== null && Number.isFinite(mp)) ? `${mp.toFixed(0)}%` : 'N/A';
            }
            if (perfDisk) {
                const dp = m.disk && m.disk.percent !== undefined ? Number(m.disk.percent) : null;
                perfDisk.textContent = (dp !== null && Number.isFinite(dp)) ? `${dp.toFixed(0)}%` : 'N/A';
            }

            const ts = (m.timestamp !== undefined && m.timestamp !== null) ? Number(m.timestamp) : (Date.now() / 1000);
            if (m.disk_io && m.disk_io.read_bytes !== undefined && m.disk_io.write_bytes !== undefined) {
                if (lastDiskIo && lastDiskIoTs) {
                    const dt = Math.max(0.001, ts - lastDiskIoTs);
                    const rbps = (Number(m.disk_io.read_bytes) - Number(lastDiskIo.read_bytes)) / dt;
                    const wbps = (Number(m.disk_io.write_bytes) - Number(lastDiskIo.write_bytes)) / dt;
                    if (perfDiskIo) perfDiskIo.textContent = `读 ${formatBytesPerSec(rbps)} | 写 ${formatBytesPerSec(wbps)}`;
                } else {
                    if (perfDiskIo) perfDiskIo.textContent = '';
                }
                lastDiskIo = { read_bytes: Number(m.disk_io.read_bytes), write_bytes: Number(m.disk_io.write_bytes) };
                lastDiskIoTs = ts;
            } else {
                if (perfDiskIo) perfDiskIo.textContent = '';
            }
        } catch (e) {
            if (perfDiskIo) perfDiskIo.textContent = '监控不可用';
        }
    }

    pollPerf();
    setInterval(pollPerf, 2000);
    
    // Generic View Content Function
    async function viewContent(type, filename) {
        try {
            // Map type to directory name
            // type: skills -> data/skills
            // type: knowledge -> data/knowledge
            // type: vulndb -> data/vulndb
            // type: reports -> data/reports
            
            // The file server is mounted at /files/
            // So url is /files/{type}/{filename}
            
            // Fix: filename might be just 'SQL Injection.md' but actually it's inside data/skills/SQL Injection.md
            // The list API returned 'name' which is the filename.
            // If the backend list_skills just returns filenames, then /files/skills/filename works if flattened.
            // But verify if sync flattened them. Yes, sync_data.py flattened them to data/skills/folder_name.md
            
            const res = await fetch(`/files/${type}/${encodeURIComponent(filename)}`);
            if (!res.ok) throw new Error('Failed to fetch content');
            
            const text = await res.text();
            
            document.getElementById('reportModalTitle').textContent = filename;
            document.getElementById('reportModalBody').innerHTML = marked.parse(text);
            reportModal.style.display = 'block';
            
        } catch (err) {
            alert('无法加载内容: ' + err.message);
        }
    }

    // === Settings Logic ===
    async function loadConfig() {
        try {
            const res = await fetch('/api/config');
            const config = await res.json();
            if (appVersionBadge && config.app_version) {
                appVersionBadge.textContent = `v${config.app_version}`;
            }

            const providerModels = {
                deepseek: [
                    { value: 'deepseek-chat', label: 'DeepSeek-Chat' },
                    { value: 'deepseek-reasoner', label: 'DeepSeek-reasoner' },
                ],
                openai: [
                    { value: 'gpt-5.2', label: 'ChatGPT-5.2' },
                    { value: 'gpt-5.2-pro', label: 'ChatGPT-5.2Pro' },
                ],
            };

            const renderModels = (provider, selectedValue) => {
                if (!aiModelSelect) return;
                aiModelSelect.innerHTML = '';
                (providerModels[provider] || []).forEach((m) => {
                    const opt = document.createElement('option');
                    opt.value = m.value;
                    opt.textContent = m.label;
                    aiModelSelect.appendChild(opt);
                });
                if (selectedValue) aiModelSelect.value = selectedValue;
                if (!aiModelSelect.value && aiModelSelect.options.length > 0) {
                    aiModelSelect.value = aiModelSelect.options[0].value;
                }
            };

            const updateApiKeyUi = (provider) => {
                const deepseekSet = (config.deepseek_is_set !== undefined) ? !!config.deepseek_is_set : !!config.is_set;
                const openaiSet = !!config.openai_is_set;
                const isSet = provider === 'openai' ? openaiSet : deepseekSet;

                if (apiKeyLabel) apiKeyLabel.textContent = provider === 'openai' ? 'OpenAI API Key' : 'DeepSeek API Key';
                if (apiKeyHint) apiKeyHint.textContent = provider === 'openai' ? '用于访问 OpenAI 模型的 API Key' : '用于访问 DeepSeek 模型的 API Key';
                if (apiKeyInput) {
                    apiKeyInput.value = '';
                    apiKeyInput.placeholder = isSet ? '已配置（留空则不修改）' : 'sk-...';
                }
                if (aiBaseUrlInput) {
                    aiBaseUrlInput.value = '';
                    const v = provider === 'openai' ? (config.openai_base_url || '') : (config.deepseek_base_url || '');
                    aiBaseUrlInput.value = v;
                    aiBaseUrlInput.placeholder = provider === 'openai' ? 'https://api.openai.com/v1' : 'https://api.deepseek.com/v1';
                }
            };

            const provider = (config.ai_provider || 'deepseek');
            if (aiProviderSelect) {
                aiProviderSelect.value = provider;
            }
            renderModels(provider, config.ai_model);
            updateApiKeyUi(provider);

            if (ocrConfigHint) {
                const deepseekSet = (config.deepseek_is_set !== undefined) ? !!config.deepseek_is_set : !!config.is_set;
                if (provider === 'openai' && !deepseekSet && !config.ocr_is_set) {
                    ocrConfigHint.textContent = 'OCR 使用云端 DeepSeek-OCR-2：若未配置 DeepSeek Key，请选择“单独配置 OCR Key”并填写。';
                } else {
                    ocrConfigHint.textContent = 'OCR 使用云端 DeepSeek-OCR-2，可选独立 Key（留空则复用 DeepSeek Key）。';
                }
            }

            if (aiProviderSelect) {
                aiProviderSelect.onchange = () => {
                    const p = aiProviderSelect.value || 'deepseek';
                    renderModels(p, null);
                    updateApiKeyUi(p);
                    if (ocrConfigHint) {
                        const deepseekSet = (config.deepseek_is_set !== undefined) ? !!config.deepseek_is_set : !!config.is_set;
                        if (p === 'openai' && !deepseekSet && !config.ocr_is_set) {
                            ocrConfigHint.textContent = 'OCR 使用云端 DeepSeek-OCR-2：若未配置 DeepSeek Key，请选择“单独配置 OCR Key”并填写。';
                        } else {
                            ocrConfigHint.textContent = 'OCR 使用云端 DeepSeek-OCR-2，可选独立 Key（留空则复用 DeepSeek Key）。';
                        }
                    }
                };
            }

            if (ocrApiKeyInput) {
                ocrApiKeyInput.value = '';
                ocrApiKeyInput.placeholder = config.ocr_is_set ? '已配置（留空则不修改）' : 'sk-...';
            }

            if (ocrKeyModeSelect && ocrKeySection) {
                ocrKeyModeSelect.value = config.ocr_is_set ? 'separate' : 'reuse';
                ocrKeySection.style.display = (ocrKeyModeSelect.value === 'separate') ? 'block' : 'none';
                ocrKeyModeSelect.onchange = () => {
                    const mode = ocrKeyModeSelect.value || 'reuse';
                    ocrKeySection.style.display = (mode === 'separate') ? 'block' : 'none';
                    if (mode !== 'separate' && ocrApiKeyInput) {
                        ocrApiKeyInput.value = '';
                    }
                };
            }
            if (ocrBaseUrlInput && (config.deepseek_ocr_base_url !== undefined)) ocrBaseUrlInput.value = config.deepseek_ocr_base_url || '';
            if (ocrModelInput && (config.deepseek_ocr_model !== undefined)) ocrModelInput.value = config.deepseek_ocr_model || '';
            if (ocrTimeoutInput && (config.deepseek_ocr_timeout !== undefined)) ocrTimeoutInput.value = config.deepseek_ocr_timeout || '';
            if (config.max_steps) maxStepsInput.value = config.max_steps;
            if (auditLogMaxRowsInput && (config.audit_log_max_rows !== undefined)) {
                auditLogMaxRowsInput.value = String(config.audit_log_max_rows || 10000);
            }
            if (config.proxy_url) proxyUrlInput.value = config.proxy_url;
            if (config.language) languageSelect.value = config.language;
            if (lhostInput && (config.ai_lhost !== undefined)) lhostInput.value = config.ai_lhost || '';

            if (toolWorkdirModeSelect && (config.tool_workdir_mode !== undefined)) {
                toolWorkdirModeSelect.value = config.tool_workdir_mode || 'project';
                if (!toolWorkdirModeSelect.value && toolWorkdirModeSelect.options.length > 0) {
                    toolWorkdirModeSelect.value = toolWorkdirModeSelect.options[0].value;
                }
            }
            if (toolMaxOutputCharsInput && (config.tool_max_output_chars !== undefined)) {
                toolMaxOutputCharsInput.value = (config.tool_max_output_chars !== null && config.tool_max_output_chars !== undefined)
                    ? String(config.tool_max_output_chars)
                    : '';
            }
            const updateDockerSection = () => {
                if (!toolSandboxSelect || !toolDockerSection) return;
                const mode = toolSandboxSelect.value || 'process';
                toolDockerSection.style.display = (mode === 'docker') ? 'block' : 'none';
            };
            if (toolSandboxSelect && (config.tool_sandbox !== undefined)) {
                toolSandboxSelect.value = config.tool_sandbox || 'process';
                if (!toolSandboxSelect.value && toolSandboxSelect.options.length > 0) {
                    toolSandboxSelect.value = toolSandboxSelect.options[0].value;
                }
                toolSandboxSelect.onchange = updateDockerSection;
                updateDockerSection();
            }
            if (toolDockerImageInput && (config.tool_docker_image !== undefined)) toolDockerImageInput.value = config.tool_docker_image || '';
            if (toolDockerNetworkSelect && (config.tool_docker_network !== undefined)) {
                toolDockerNetworkSelect.value = config.tool_docker_network || 'bridge';
                if (!toolDockerNetworkSelect.value && toolDockerNetworkSelect.options.length > 0) {
                    toolDockerNetworkSelect.value = toolDockerNetworkSelect.options[0].value;
                }
            }
            if (toolDockerMemoryInput && (config.tool_docker_memory !== undefined)) toolDockerMemoryInput.value = config.tool_docker_memory || '';
            if (toolDockerPidsLimitInput && (config.tool_docker_pids_limit !== undefined)) toolDockerPidsLimitInput.value = config.tool_docker_pids_limit || '';
            
            await loadNetworkInterfaces(config);
        } catch (err) {
            console.error('Load config failed:', err);
        }
    }

    async function loadNetworkInterfaces(config) {
        if (!bindInterfaceSelect) return;
        try {
            const res = await fetch('/api/network/interfaces');
            const data = await res.json();

            bindInterfaceSelect.innerHTML = '';
            (data.interfaces || []).forEach((i) => {
                const opt = document.createElement('option');
                const ip = i.ipv4 ? ` - ${i.ipv4}` : '';
                const state = i.up === false ? ' (down)' : '';
                opt.value = i.name;
                opt.textContent = `${i.name}${ip}${state}`;
                opt.dataset.ipv4 = i.ipv4 || '';
                opt.dataset.up = i.up === true ? '1' : (i.up === false ? '0' : '');
                bindInterfaceSelect.appendChild(opt);
            });

            const wanted = (config && config.ai_bind_interface) ? config.ai_bind_interface : data.selected;
            if (wanted) bindInterfaceSelect.value = wanted;
            if (!bindInterfaceSelect.value && bindInterfaceSelect.options.length > 0) {
                bindInterfaceSelect.value = bindInterfaceSelect.options[0].value;
            }

            const updateHints = () => {
                const selectedOpt = bindInterfaceSelect.selectedOptions[0];
                const selectedIp = selectedOpt ? (selectedOpt.dataset.ipv4 || '') : '';
                const iface = bindInterfaceSelect.value || '';
                if (bindInterfaceHint) {
                    bindInterfaceHint.textContent = iface ? `当前选择：${iface}${selectedIp ? `（IPv4: ${selectedIp}）` : '（无 IPv4）'}` : '';
                }
                const manual = lhostInput ? (lhostInput.value || '').trim() : '';
                const effective = manual || selectedIp || '127.0.0.1';
                if (effectiveLhostHint) {
                    effectiveLhostHint.textContent = manual
                        ? `当前将使用手动 LHOST：${effective}`
                        : `未填写 LHOST，默认使用所选网卡 IP：${effective}`;
                }
            };

            if (bindInterfaceSelect) bindInterfaceSelect.addEventListener('change', updateHints);
            if (lhostInput) lhostInput.addEventListener('input', updateHints);
            updateHints();
        } catch (err) {
            console.error('Load network interfaces failed:', err);
        }
    }
    
    if(saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', async () => {
            const config = {
                ai_provider: aiProviderSelect ? aiProviderSelect.value : undefined,
                ai_model: aiModelSelect ? aiModelSelect.value : undefined,
                max_steps: parseInt(maxStepsInput.value),
                proxy_url: proxyUrlInput.value,
                language: languageSelect.value,
                ai_bind_interface: bindInterfaceSelect ? bindInterfaceSelect.value : undefined,
                ai_lhost: lhostInput ? (lhostInput.value || '').trim() : undefined
            };
                    if (aiBaseUrlInput) {
                        const p = (aiProviderSelect && aiProviderSelect.value) ? aiProviderSelect.value : 'deepseek';
                        const v = (aiBaseUrlInput.value || '').trim();
                        if (p === 'openai') {
                            config.openai_base_url = v;
                        } else {
                            config.deepseek_base_url = v;
                        }
                    }
            if (apiKeyInput && apiKeyInput.value) {
                const provider = (aiProviderSelect && aiProviderSelect.value) ? aiProviderSelect.value : 'deepseek';
                if (provider === 'openai') {
                    config.openai_api_key = apiKeyInput.value;
                } else {
                    config.deepseek_api_key = apiKeyInput.value;
                }
            }
            if (ocrKeyModeSelect) {
                const mode = ocrKeyModeSelect.value || 'reuse';
                if (mode === 'separate') {
                    if (ocrApiKeyInput && ocrApiKeyInput.value) {
                        config.deepseek_ocr_api_key = ocrApiKeyInput.value;
                    }
                } else {
                    config.deepseek_ocr_api_key = '';
                }
            }

            if (ocrBaseUrlInput) config.deepseek_ocr_base_url = (ocrBaseUrlInput.value || '').trim();
            if (ocrModelInput) config.deepseek_ocr_model = (ocrModelInput.value || '').trim();
            if (ocrTimeoutInput) config.deepseek_ocr_timeout = (ocrTimeoutInput.value || '').trim();

            if (toolWorkdirModeSelect) config.tool_workdir_mode = toolWorkdirModeSelect.value;
            if (toolMaxOutputCharsInput) config.tool_max_output_chars = parseInt(toolMaxOutputCharsInput.value);
            if (toolSandboxSelect) config.tool_sandbox = toolSandboxSelect.value;
            if (toolDockerImageInput) config.tool_docker_image = (toolDockerImageInput.value || '').trim();
            if (toolDockerNetworkSelect) config.tool_docker_network = toolDockerNetworkSelect.value;
            if (toolDockerMemoryInput) config.tool_docker_memory = (toolDockerMemoryInput.value || '').trim();
            if (toolDockerPidsLimitInput) config.tool_docker_pids_limit = (toolDockerPidsLimitInput.value || '').trim();
            if (auditLogMaxRowsInput) {
                const v = (auditLogMaxRowsInput.value || '').trim();
                if (v) {
                    const n = parseInt(v);
                    if (Number.isFinite(n) && n >= 1 && n <= 100000) {
                        config.audit_log_max_rows = n;
                    } else {
                        alert('日志存储上限条数必须为 1 - 100000 的整数');
                        return;
                    }
                }
            }

            try {
                emitUiAudit('settings_save', {
                    ai_provider: config.ai_provider,
                    ai_model: config.ai_model,
                    max_steps: config.max_steps,
                    has_proxy: Boolean((config.proxy_url || '').trim()),
                    has_api_key: Boolean(apiKeyInput && apiKeyInput.value),
                    audit_log_max_rows: config.audit_log_max_rows
                });
            } catch (e) {}
            
            try {
                const res = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });
                
                if (res.ok) {
                    alert('设置已保存');
                } else {
                    let msg = '保存失败';
                    try {
                        const data = await res.json();
                        if (data && (data.error || data.message)) msg = data.error || data.message;
                    } catch {}
                    alert(msg);
                }
            } catch (err) {
                console.error(err);
                alert('保存出错');
            }
        });
    }
});
