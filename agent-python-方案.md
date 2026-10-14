# 智慧牧场 AI Agent 诊断服务 Python 落地方案

## 1. 核心设计目标

1. **强数据支撑与来源追溯 (Evidence Traceability)**：
   * 所有诊断结论、疑似疾病判断和处置建议，必须严格绑定具体的数据证据项（如：`EV-01: 体温持续>39.5℃`、`EV-02: 反刍同比下降35%`、`KB-03: 隐性乳房炎 SOP 第 2.1 节`）。
2. **模块化与 MCP/Tool 工具解耦**：
   * 采用标准 Tool 接口和 MCP (Model Context Protocol) 客户端机制，将底层 IoT/MySQL/VectorDB 适配解耦。
3. **LangGraph 确切图状态流转与 Human-in-the-Loop**：
   * 采用 LangGraph `StateGraph` 控制流程（告警解析 -> 工具数据采集 -> 证据汇总 -> 诊断合成 -> 人工确认 Interrupt -> 工单派发）。
4. **死循环熔断与数据缺失降级告知**：
   * 双重熔断（`recursion_limit` 与 `loop_count` 判重），缺失数据时拒绝硬猜，显式输出 `INSUFFICIENT_EVIDENCE` 状态及人工排查建议。

---

## 2. 项目目录结构

```
cow-agent/
├── agent-方案.md                   # 初始 Golang+Python 系统架构方案
├── agent-python-方案.md            # Python Agent 服务落地详细方案
├── requirements.txt                # 项目依赖配置文件
├── start.ps1                       # Windows PowerShell 一键启动脚本
├── run.bat                         # Windows CMD 一键启动脚本
├── README.md                       # 服务说明与使用指南
│
├── config/                         # 系统配置
│   ├── __init__.py
│   ├── settings.py                 # 环境变量与服务配置
│   └── prompts.py                  # Prompt 模板与思维链约束
│
├── src/                            # 核心业务代码
│   ├── __init__.py
│   ├── main.py                     # FastAPI 服务入口
│   │
│   ├── graph/                      # LangGraph 状态机
│   │   ├── __init__.py
│   │   ├── state.py                # Agent 共享状态定义
│   │   ├── workflow.py             # 状态图拓扑与条件路由
│   │   └── nodes/                  # 图节点实现
│   │       ├── __init__.py
│   │       ├── parse_node.py       # 告警与意图解析
│   │       ├── evidence_node.py    # 证据汇总与提炼
│   │       ├── rag_node.py         # 兽医 SOP 知识检索
│   │       ├── diagnose_node.py    # 诊断合成 (绑定数据支撑)
│   │       └── hitl_node.py        # 人工确认中断与恢复
│   │
│   ├── schemas/                    # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── request.py              # 请求 Schema
│   │   ├── response.py             # 诊断报告 Schema
│   │   └── evidence.py             # 证据项 Schema
│   │
│   ├── tools/                      # 工具与 MCP 适配
│   │   ├── __init__.py
│   │   ├── registry.py             # 工具注册中心
│   │   ├── iot_tools.py            # IoT 查询工具
│   │   ├── cow_profile_tools.py    # 档案与病历工具
│   │   ├── rag_tools.py            # 向量 SOP 工具
│   │   └── mcp_clients/            # MCP 协议客户端
│   │       ├── __init__.py
│   │       ├── base_mcp_client.py   # MCP 协议基类
│   │       ├── iot_mcp_client.py    # IoT MCP 适配
│   │       ├── mysql_mcp_client.py  # MySQL MCP 适配
│   │       └── rag_mcp_client.py    # RAG MCP 适配
│   │
│   └── utils/                      # 通用工具
│       ├── __init__.py
│       ├── logger.py               # 规范结构化日志
│       └── guardrails.py           # 用药剂量与红线护栏
│
└── tests/                          # 单元测试
    ├── __init__.py
    ├── test_graph.py               # 状态机测试
    └── test_tools.py               # 工具链测试
```

---

## 3. 代码约束规范

1. **函数参数限制**：单函数/方法形参入参最多不超过 5 个。
2. **文件行数限制**：单文件行数严格控制在 200 行以内。
3. **结构化日志**：使用 `loguru` 打印带有 session_id、cow_id、tool_name 等关键参数的日志。
4. **注释覆盖**：所有类、主要函数、模块均包含详尽文档字符串与类型注解。
