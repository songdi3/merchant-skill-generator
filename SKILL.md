---
name: merchant-skill-generator
description: 商家 AI 技能生成器。帮助生活服务类商家（餐厅、奶茶店、咖啡馆、健身房、美容院、教育培训等）快速创建一个专属的 AI 技能包（.skill 文件）。支持通过 MCP 实时获取美团/大众点评商家数据，自动解析门店信息并生成技能，商家只需提供店铺链接即可。触发词：创建一个商家技能、帮我的店做一个 AI、生成技能包、做个店铺 AI 助手、帮我生成一个店铺 AI。
---

# 商家 AI 技能生成器

帮助生活服务类商家快速生成专属 AI 技能的工具。

## 工作原理

商家与 AI 对话 → AI 引导填写配置问卷 → 自动生成可安装的 `.skill` 文件 → 一键安装即可使用

## 适用商家类型

餐厅/饺子馆/火锅店/奶茶店/咖啡馆/健身房/美容院/教育培训/便利店/药店/宠物店/鲜花店等生活服务类商家

## 核心 MCP 工具

本技能通过 MCP 协议实时调用外部服务，生成技能时优先使用工具自动抓取数据。

| 工具 | 功能 | 使用场景 |
|------|------|---------|
| `fetch_meituan_shop` | 自动抓取美团/点评商家数据 | 商家只提供一个链接，AI 自动解析全部信息 |
| `fetch_meituan_queue` | 查询美团排队状态 | 商家有排队需求时 |
| `generate_merchant_skill` | 生成并打包 skill 文件 | 收集完信息后一键生成 |
| `package_skill` | 打包 .skill 文件 | 交付给商家前 |

### 推荐工作流：发链接 → 自动生成

**Step 1**：商家发来美团/点评店铺链接
```
fetch_meituan_shop(source="meituan_url", value="https://www.meituan.com/cate/xxx")
```

**Step 2**：AI 自动解析所有商家信息（店名、地址、价格、套餐……）

**Step 3**：一键生成 skill
```
generate_merchant_skill(merchant={...}, stores=[...], recommendations=[...], data_mode="static")
```

**Step 4**：打包交付
```
package_skill(skill_name="xxx")
```

商家不需要手动填表！只需发个链接或店名，AI 全部搞定。

### Step 0：确认商家意图

商家说"创建一个商家技能"或类似意图时触发本技能。

先友好问候，然后请商家选择技能语言：

> 🏪 欢迎使用商家 AI 技能生成器！
> 
> 告诉我您的**店铺名称**和**所在城市**，我来帮您做一个专属的 AI 助手技能。
> 
> 同时请告诉我您希望的技能语言：中文 / English

### Step 1：收集必填信息

使用 `references/questionnaire.md` 引导商家完成信息收集。

**必填字段（无则跳过）：**
- 商家名称
- 城市/区域
- 行业类型
- 营业时间

**商家回答后，记录商家提供的信息，按 `references/questionnaire.md` 的格式整理。**

### Step 2：收集选填能力

根据商家行业，推荐可选模块（见 `references/questionnaire.md` 能力矩阵）。

常用可选模块：
- 🍜 **菜单/服务查询**：推荐菜品、特色服务
- 📍 **门店信息**：地址、导航、停车信息
- ⏰ **营业时间**：工作日/周末/节假日时间
- 📞 **联系方式**：电话、微信公众号
- 🎫 **在线预约/排队**：需商家提供美团/大众点评门店ID
- 🛵 **外卖服务**：配送范围、起送价
- 📢 **最新公告**：优惠活动、门店通知
- 💡 **常见问题**：FAQ

### Step 3：选择数据模式

询问商家选择哪种模式：

**静态模式**（默认）：
> "好的，您的技能将使用静态数据，所有信息内嵌在文件中，完全离线可用。"

**MCP 模式**（商家有接口能力）：
> "您的技能将支持实时数据查询。需要提供 MCP 端点 URL 和工具列表。"
> 参考 `references/mcp_setup.md` 引导商家完成 MCP 配置。

如果商家选择 MCP：
1. 引导商家提供 MCP 端点 URL
2. 确认工具列表（至少包含 store_info + recommendations）
3. 验证接口可用性：
```bash
curl -X POST <MCP_URL> -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```
4. 将 MCP 配置填入 JSON 配置中的 `mcp_config` 字段

### Step 4：生成技能

调用脚本生成：

```bash
python3 scripts/generate_skill.py --config <商家配置JSON>
```

脚本输出：
- 生成的 skill 目录路径
- `skill.json`（元数据）
- `SKILL.md`（核心文档）
- 各类参考文献（references/）
- 脚本文件（scripts/）

### Step 5：打包交付

```bash
bash scripts/package_skill.sh <skill-name>
```

生成 `.skill` 文件交给商家。

### Step 6：安装指引

告知商家安装命令：

```bash
clawhub install <skill-name>
# 或手动安装
clawhub install ./dist/<skill-name>.skill
```

## 注意事项

- **数据安全**：商家填写的信息仅用于生成技能文件，不上传到任何第三方
- **盲区处理**：超出生活服务范围的能力（如金融、医疗、法律咨询）不承接
- **brand_prompt 原则**：生成的技能需包含品牌调性指南，让 AI 助手说话风格与商家一致
- **Fallback 机制**：MCP 不可用时，必须有静态数据兜底回复

## 文件结构

```
merchant-skill-generator/
├── SKILL.md                        ← 本文件
└── references/
    ├── questionnaire.md             ← 商家信息收集问卷（含 MCP 模式）
    ├── mcp_setup.md                 ← MCP 接入指南（新增）
    ├── skill_template.md            ← 生成的 SKILL.md 模板
    ├── skill_json_template.json     ← 生成的 skill.json 模板
    └── brand_prompt_guide.md        ← 品牌调性指南写法
└── scripts/
    ├── generate_skill.py             ← 核心生成脚本（支持 MCP 配置）
    └── package_skill.sh              ← 打包脚本
```
