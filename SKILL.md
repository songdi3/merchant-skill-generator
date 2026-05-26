---
name: merchant-skill-generator
description: 商家 AI 技能生成器 v2.0。帮助生活服务类商家（餐厅、健身房、美容院、药店、便利店等）快速创建完整的专属 AI 技能包（.skill 文件）。生成技能包含 9+ 工具函数，覆盖顾客各种场景（查询/外卖/排队/预约等）。触发词：创建一个商家技能、帮我的店做一个 AI、生成技能包、做个店铺 AI 助手、帮我生成一个店铺 AI。
---

# 商家 AI 技能生成器 v2.0

帮助生活服务类商家快速生成**完整、专业、能真正服务顾客**的 AI 技能。

## 目标：生成和金谷园一样完整的技能

参考标杆：[金谷园饺子馆 skill](https://github.com/JinGuYuan/jinguyuan-dumpling-skill)（9个工具函数，覆盖顾客所有场景）

**v2.0 核心升级：**
- ✅ 自动生成 **9+ 工具函数**（不是只有 4-5 个）
- ✅ 覆盖顾客 **所有常见场景**（地址/外卖/排队/预约/ Wi-Fi /会员/菜品配方等）
- ✅ 行业专属工具（餐饮/健身/美容/零售/医疗）
- ✅ 自动从服务清单生成对应工具，不遗漏任何服务

## 适用商家类型

| 行业 | 可生成的工具函数数 |
|------|-----------------|
| 餐饮（餐厅/奶茶/咖啡/火锅） | 最多 12 个（外卖/排队/预约/ Wi-Fi /配方/打包/会员等） |
| 健身/运动 | 最多 7 个（课程/教练/会员/预约/体测等） |
| 美容/美发 | 最多 7 个（服务价格/设计师/预约/会员/作品等） |
| 零售/便利店 | 最多 5 个（商品/库存/促销/配送） |
| 医疗/健康 | 最多 5 个（科室/医生/挂号/排队） |
| 其他生活服务 | 基础 4 个（信息/推荐/联系/公告） |

## 工具函数库（按行业）

### 通用工具（所有商家都有）
- `get_store_info` - 门店信息（地址/营业时间/电话/交通）
- `get_recommendations` - 推荐服务/商品
- `get_contact_info` - 联系方式（电话/微信/地图）
- `get_latest_news` - 最新动态/公告/优惠

### 餐饮行业额外工具
- `get_delivery_info` - 外卖配送（平台/范围/起送价）
- `get_pickup_link` - 到店自取（小程序下单）
- `get_menu` - 菜单/价格查询
- `get_queue_info` - 排队取号（美团实时）
- `get_reservation_info` - 座位/包间预订
- `get_wifi_info` - 店内 Wi-Fi
- `get_packaging_info` - 生鲜打包/外带/烹饪教程
- `get_membership_info` - 会员权益/优惠券
- `get_recipes` - 菜品配方公开

### 健身行业额外工具
- `get_courses` - 课程/团课介绍
- `get_coaches` - 教练团队介绍
- `get_booking_info` - 预约私教/课程
- `get_assessment_info` - 体测/身体评估

### 美容行业额外工具
- `get_services` - 服务项目/价格表
- `get_stylists` - 设计师/美容师介绍
- `get_gallery` - 客户作品展示

### 零售/便利店额外工具
- `get_products` - 商品列表/热销/新品
- `get_inventory` - 库存查询
- `get_promotions` - 促销/特价/优惠券

### 医疗行业额外工具
- `get_departments` - 科室/服务介绍
- `get_doctors` - 医生/专家/出诊时间

## 生成流程

### Step 0：确认商家意图

商家说"创建一个商家技能"或类似意图时触发。

**开场白：**
> 🦞 欢迎使用商家 AI 技能生成器 v2.0！
>
> 告诉我您的**店铺名称**和**所在城市**，我来帮您做一个专属的 AI 助手技能。
> 
> 同时请告诉我您希望的技能语言：**中文** / English

### Step 1：引导填写 v2 问卷

使用 `references/questionnaire_v2.md` 引导商家完成信息收集。

**v2 问卷核心改进：**
1. **服务清单逐项确认** —— 不是问"你有没有特殊需求"，而是列出所有可能的服务让商家逐项确认
2. **行业专属章节** —— 餐饮/健身/美容/零售/医疗各有专属问题
3. **小程序/App 询问** —— 有小程序才有过客自取功能
4. **常见问题清单** —— 商家列出 Top5 问题，AI 针对性优化
5. **完整触发场景** —— 每个工具都有对应"用户会怎么问"

### Step 2：生成技能

```bash
python3 scripts/generate_skill_v2.py --config-file <配置文件>
```

脚本输出：
- 生成的 skill 目录路径
- 工具函数数量
- `skill.json`（完整元数据 + 所有工具函数）
- `SKILL.md`（完整文档 + 所有服务章节）
- `references/store_data.md`（静态兜底数据）
- 美团排队文件（如需要）

### Step 3：交付

```bash
bash scripts/package_skill.sh <skill-name>
```

生成 `.skill` 文件 + 飞书文档交给商家。

## 注意事项

- **服务清单是关键** —— 商家不填写服务清单，生成的技能会缺少工具函数
- **引导时多问一句** —— "你们有 Wi-Fi 吗？""支持外卖吗？""有小程序吗？"
- **不确定就默认开启** —— 商家不确定的服务，标注为"可后续添加"
- **盲区处理** —— 超出工具范围时，诚实告知并引导到店或致电

## 文件结构

```
merchant-skill-generator/
├── SKILL.md                        ← 本文件
├── references/
│   ├── questionnaire_v2.md         ← v2 问卷（服务清单式）
│   ├── questionnaire.md            ← v1 问卷（保留兼容）
│   ├── mcp_setup.md                ← MCP 接入指南
│   ├── skill_template.md           ← v1 SKILL.md 模板
│   └── brand_prompt_guide.md       ← 品牌调性指南
└── scripts/
    ├── generate_skill_v2.py        ← v2 核心生成脚本（推荐使用）
    ├── generate_skill.py            ← v1 生成脚本（保留兼容）
    └── package_skill.sh            ← 打包脚本
```
