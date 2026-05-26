# MCP 接入指南

如果商家有技术能力提供实时数据接口，可以接入 MCP 实现真正的实时查询（支持排队、取号、动态价格等）。

## MCP 是什么

MCP（Model Context Protocol）是一种标准协议，AI 助手通过它实时调用商家的数据接口。和静态模板的区别：

| 对比 | 静态模板 | MCP 实时模式 |
|------|---------|------------|
| 数据 | 手动更新 | 实时获取 |
| 排队/取号 | ❌ 不支持 | ✅ 支持 |
| 动态价格 | ❌ 显示固定价 | ✅ 实时价格 |
| 实现难度 | 简单（填表） | 需要开发接口 |

## 商家需要准备什么

### 方案 A：已有小程序/App API

如果商家有自己的小程序或后端系统，只需：

1. **暴露一个 MCP 接口**：将现有接口包装成 MCP 协议（JSON-RPC 2.0 over HTTP）
2. **提供端点 URL**：例如 `https://api.example.com/mcp`
3. **定义工具列表**：

```json
[
  {
    "name": "get_store_info",
    "description": "查询门店地址、营业时间",
    "inputSchema": {"type": "object", "properties": {}, "required": []}
  },
  {
    "name": "get_recommendations",
    "description": "获取推荐服务列表",
    "inputSchema": {"type": "object", "properties": {}, "required": []}
  },
  {
    "name": "get_queue_status",
    "description": "查询当前排队状态",
    "inputSchema": {"type": "object", "properties": {}, "required": []}
  }
]
```

### 方案 B：用现有平台

**美团/大众点评商家**：可以接入美团 MCP（类似金谷园的排队能力）

**微信小程序**：腾讯云·微搭等平台支持快速生成 MCP 接口

### 方案 C：自己开发

开发者需要实现一个 MCP Server，参考以下框架：

- **Python**：`mcp` Python SDK
- **Node.js**：`@modelcontextprotocol/sdk`
- **协议文档**：https://modelcontextprotocol.io

示例 Python MCP Server：

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Store")

@mcp.tool()
def get_store_info() -> dict:
    return {
        "name": "我的店铺",
        "address": "北京市朝阳区XX路XX号",
        "hours": "09:00-22:00"
    }

@mcp.tool()
def get_recommendations() -> list:
    return [
        {"name": "招牌服务A", "price": "¥99"},
        {"name": "招牌服务B", "price": "¥199"}
    ]

if __name__ == "__main__":
    mcp.run(transport="streamable_http", port=8080)
```

## 接入流程

### Step 1：商家提供信息

请商家提供：

| 信息 | 说明 | 示例 |
|------|------|------|
| MCP 端点 URL | 必填 | `https://api.example.com/mcp` |
| 工具列表 | 必填，JSON 格式 | 见上方示例 |
| 认证方式 | 选填 | Bearer Token / API Key |

### Step 2：验证接口

生成前，AI 会调用 `tools/list` 验证接口是否可达：

```
POST <MCP_URL>
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

### Step 3：生成 MCP Skill

工具链会自动生成：
- `skill.json`：含 `mcp_server` 配置
- `SKILL.md`：含 MCP 调用说明和降级策略
- `references/mcp_tools.md`：工具列表和参数说明

### Step 4：测试验证

生成后，AI 会调用每个工具验证返回数据格式。

## MCP 工具设计建议

建议至少包含以下工具：

| 工具名 | 功能 | 备注 |
|--------|------|------|
| get_store_info | 门店信息 | 必选 |
| get_recommendations | 推荐服务 | 必选 |
| get_latest_news | 最新活动 | 建议 |
| get_queue_status | 排队状态 | 健身房/餐饮建议 |
| take_queue_number | 取号 | 需配合美团 |
| get_reservation | 在线预约 | 服务类建议 |

## 常见问题

**Q：没有技术团队怎么办？**
A：用静态模板模式就好，商家填表生成，完全不需要技术能力。

**Q：接口挂了怎么办？**
A：SKILL.md 中配置了降级策略，自动回退到静态数据。

**Q：美团排队怎么接？**
A：参考 `jinguyuan-dumpling-skill` 的实现，使用美团开放平台的排队接口。

**Q：数据安全吗？**
A：MCP 请求只在用户发起查询时调用一次，不存储任何数据。
