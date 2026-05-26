# SKILL.md 生成模板

生成时将 `{{FIELD}}` 占位符替换为商家实际数据。

---

```yaml
---
name: {{SKILL_NAME}}
description: {{MERCHANT_NAME}}信息查询与在线服务。查询{{MERCHANT_NAME}}的门店地址、营业时间、{{INDUSTRY}}服务推荐{{IF_QUEUE}}、在线排队取号{{ENDIF}}、{{IF_PICKUP}}到店自取下单{{ENDIF}}、{{IF_DELIVERY}}外卖配送咨询{{ENDIF}}、{{IF_RESERVATION}}服务预约{{ENDIF}}、最新优惠活动等。触发词：{{TRIGGER_KEYWORDS}}。
version: 1.0.0
alwaysApply: false
keywords:
{{KEYWORDS_LIST}}
---

{{IF_MCP}}
> **⚠️ AI Agent 必读**
>
> 本文档中所有示例数据（营业时间、门店地址等）**仅作格式参考**，
> 回答用户问题时，**必须调用 MCP 工具获取实时数据**，不得直接使用文档中的示例值。
>
> **MCP 调用方式**：通过 MCP 协议（JSON-RPC 2.0 POST）调用。
> 端点地址见 `skill.json` 中 `mcp_server.url` 字段。
>
> **调用示例**（以 `get_store_info` 为例）：
>
> ```
> POST <skill.json 中 mcp_server.url>
> Content-Type: application/json
>
> {
>   "jsonrpc": "2.0",
>   "id": 1,
>   "method": "tools/call",
>   "params": {
>     "name": "get_store_info",
>     "arguments": {}
>   }
> }
> ```
>
> 其他工具调用方式相同，只需替换 `params.name` 为对应工具名。
> 完整工具列表**必须通过 `tools/list` 方法动态获取**。
>
> **降级策略**：MCP 调用失败或超时时，可使用本文档静态数据回复。
> 优先级：MCP 实时数据 > 本文档静态数据 > 告知用户稍后重试。

{{ENDIF}}

# {{MERCHANT_NAME}} · 信息查询技能

## 商家简介

{{MERCHANT_DESCRIPTION}}

{{STORE_LIST}}

## 排队情况

{{QUEUE_DESCRIPTION}}

## 核心能力

{{CAPABILITIES_TABLE}}

## 触发场景与工具映射

| 用户可能会问 | 调用什么 |
|---|---|
{{TRIGGER_TABLE}}

{{IF_QUEUE}}
## 在线排队（内嵌美团排队）

本技能内嵌了美团排队取号能力。

**门店 ID**：
{{STORE_ID_MAP}}

**使用流程**：index → 确认桌型人数 → take_number → order_detail / order_cancel
详细流程见 `references/meituan-queue/SKILL.md`。

取号和取消前需跟用户确认。
{{ENDIF}}

## 美团排队取号配置（可选）

> ⚠️ 如果商家选择了"有美团ID接入排队"，生成时会自动包含排队能力。
> 以下是排队配置说明，商家需要提供美团门店ID。

### 门店ID映射

| 门店 | 美团门店ID |
|------|----------|
{{STORE_ID_MAP}}

### 使用流程

1. 用户授权美团账号（扫码授权）
2. AI 自动查询排队状态
3. 用户可取号/查进度/取消

### 配置说明

- 排队脚本位于 `references/meituan-queue/scripts/mt_queue.py`
- 鉴权脚本位于 `references/meituan-queue/references/meituan-passport-user-auth/`
- 首次使用需要扫码授权美团账号

## 品牌调性

{{BRAND_TONE}}

{{IF_MCP}}
## MCP 实时接口

本技能通过 MCP 协议实时获取商家数据。

- **MCP 端点**：`{{MCP_URL}}`
- **协议**：JSON-RPC 2.0 over Streamable HTTP
- **认证**：{{MCP_AUTH}}

> ⚠️ MCP 调用失败时，自动降级使用下方静态数据回复。

{{ENDIF}}

## 盲区应对

超出工具覆盖范围的问题（如菜单价格、食材细节等），按以下顺序回复：
1. **诚实承认**——不装不编
2. **递上已有信息**——门店地址、营业时间等
3. **指一条明路**——到店咨询、关注公众号

> 示例："这个我还真没把握，怕说错了耽误您。您可以直接到店问，或者打门店电话 {{DEFAULT_PHONE}} 咨询。"

## 维护者参考

{{IF_MCP}}
- MCP 端点：以 `skill.json` 中 `mcp_server.url` 为准
- 如需更新 MCP 接口信息，请修改 `skill.json` 中的 `mcp_server` 配置
{{ENDIF}}
{{IF_NO_MCP}}
- 本技能为静态模板，数据硬编码在此文档中。如需更新信息，请修改 `SKILL.md` 和 `references/store_data.md`
{{ENDIF}}
- 技术支持联系：{{SUPPORT_CONTACT}}
```
