# 智慧牧场 AI Agent 诊断与工单系统

基于 **Python + LangGraph** 构建的高可靠、有数据支撑追溯且具备 Human-in-the-Loop 人工确认机制的 AI Agent 诊断服务。

---

## 🌟 核心特性

1. **强数据支撑与归因追溯 (Evidence Traceability)**：
   * 所有诊断结论强制关联 `EV-01: 耳标体温`、`EV-02: 反刍降幅`、`EV-04: 既往病史` 等证据 ID。
2. **死循环熔断与数据缺失告知**：
   * 双重熔断（LangGraph `recursion_limit=8` 结合 `loop_count >= 3` 判重熔断）。
   * 数据源缺失时拒绝盲猜幻觉，显式输出 `INSUFFICIENT_EVIDENCE` 状态及人工排查建议。
3. **Human-in-the-Loop 人机协作派单**：
   * 诊断报告生成后自动挂起，由兽医确认 (`APPROVE`) 或修正后，再触发工单落库。
4. **Tool Call / MCP 适配器统一支持**：
   * 支持通过 `src/tools/registry.py` 在本地直连驱动与标准 MCP (Model Context Protocol) 适配器之间无缝切换。

---

## ⚡ 一键启动指南

在 Windows PowerShell 下直接运行主目录下的启动脚本：

```powershell
.\start.ps1
```

或 CMD 命令行下执行：

```cmd
run.bat
```

**启动流程会自动执行**：
1. 自动创建 Python `venv` 虚拟环境；
2. 自动安装 `requirements.txt` 中的依赖；
3. 自动运行 `pytest` 单元测试；
4. 启动 FastAPI REST API 服务（访问地址：`http://127.0.0.1:8000/docs`）。

---

## 🧪 单元测试

手动执行单元测试：

```powershell
.\venv\Scripts\pytest
```

---

## 📡 API 接口示例

### 1. 发起 Agent 诊断请求
* **POST** `/api/v1/agent/diagnose`
* **Request Payload**:
  ```json
  {
    "cow_id": "8892",
    "user_query": "8892号牛体温偏高且反刍下降，请进行诊断"
  }
  ```

### 2. 人工确认派单 (Human-in-the-Loop)
* **POST** `/api/v1/agent/confirm`
* **Request Payload**:
  ```json
  {
    "session_id": "sess_xxx",
    "action": "APPROVE",
    "operator_id": "VET-007",
    "modified_suggest": "隔离并补充生理盐水"
  }
  ```
