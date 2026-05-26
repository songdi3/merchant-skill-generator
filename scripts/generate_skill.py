#!/usr/bin/env python3
"""
商家技能生成器 - 核心生成脚本

用法:
    python3 generate_skill.py --config <商家配置JSON>
    python3 generate_skill.py --config-file <配置文件路径>

输入: 商家配置JSON（见 references/questionnaire.md 输出格式）
输出: 生成的 skill 目录路径 + 打包指引
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
REFERENCES_DIR = SKILL_DIR / "references"

def to_skill_name(merchant_name, language="zh"):
    """将商家名称转换为 skill 名称（纯ASCII + 连字符）"""
    pinyin_map = {
        '置':'zhi','顶':'ding','健':'jian','身':'shen','房':'fang',
        '金':'jin','谷':'gu','园':'yuan','饺':'jiao','子':'zi','馆':'guan',
        '咖':'ka','啡':'fei','奶':'nai','茶':'cha','美':'mei','容':'rong',
        '教':'jiao','育':'yu','培':'pei','训':'xun','药':'yao','店':'dian',
        '便':'bian','利':'li','超':'chao','市':'shi','宠':'chong','物':'wu',
        '花':'hua','银':'yin','行':'hang','酒':'jiu','宾':'bin','洗':'xi',
        '车':'che','修':'xiu','乐':'le','器':'qi','牙':'ya','科':'ke',
        '电':'dian','影':'ying','网':'wang','吧':'ba','理':'li','发':'fa',
        '按':'an','摩':'mo','瑜':'yu','伽':'jia','摄':'she','书':'shu',
        '餐':'can','厅':'ting','炸':'zha','酱':'jiang','面':'mian','老':'lao','王':'wang',
        '北':'bei','京':'jing','上':'shang','海':'hai','广':'guang','州':'zhou',
        '深':'shen','圳':'zhen','成':'cheng','都':'dou','南':'nan','京':'jing',
    }
    result = []
    for char in merchant_name:
        if '\u4e00' <= char <= '\u9fff':
            result.append(pinyin_map.get(char, ''))
        elif char.isalnum():
            result.append(char.lower())
    name = '-'.join([r for r in result if r])
    name = re.sub(r'-+', '-', name).lower()
    return name

def generate_keywords(merchant_name, industry, modules, language="zh"):
    """生成 keywords 数组"""
    base_keywords = []
    # 商家名分词（简单处理）
    for char in merchant_name:
        if '\u4e00' <= char <= '\u9fff':
            base_keywords.append(char)
    base_keywords.extend([merchant_name, industry])
    return list(set(base_keywords))[:20]

def generate_tools(config):
    """根据模块配置生成 tools 数组"""
    modules = config.get("modules", {})
    tools = []
    
    tool_templates = {
        "store_info": {
            "name": "get_store_info",
            "display_name": "门店信息",
            "description": "查询{MERCHANT}的门店地址、营业时间、联系电话等信息。".format(MERCHANT=config["merchant"]["name"]),
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        "recommendations": {
            "name": "get_recommendations",
            "display_name": "推荐服务",
            "description": "获取{MERCHANT}当前推荐的服务/商品列表。".format(MERCHANT=config["merchant"]["name"]),
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        "news": {
            "name": "get_latest_news",
            "display_name": "最新公告",
            "description": "获取{MERCHANT}的最新优惠活动和门店通知。".format(MERCHANT=config["merchant"]["name"]),
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        "contact": {
            "name": "get_contact_info",
            "display_name": "联系方式",
            "description": "获取{MERCHANT}的联系电话、微信公众号等联系方式。".format(MERCHANT=config["merchant"]["name"]),
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        "delivery": {
            "name": "get_delivery_info",
            "display_name": "外卖配送",
            "description": "获取{MERCHANT}的外卖配送范围、起送价等信息。".format(MERCHANT=config["merchant"]["name"]),
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        "pickup": {
            "name": "get_pickup_link",
            "display_name": "到店自取",
            "description": "获取{MERCHANT}小程序到店自取下单链接。".format(MERCHANT=config["merchant"]["name"]),
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        "queue": {
            "name": "get_queue_info",
            "display_name": "排队取号",
            "description": "获取{MERCHANT}堂食排队取号方式和当前排队状态。".format(MERCHANT=config["merchant"]["name"]),
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        "reservation": {
            "name": "get_reservation_info",
            "display_name": "服务预约",
            "description": "获取{MERCHANT}的在线预约方式和可预约服务项目。".format(MERCHANT=config["merchant"]["name"]),
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
    }
    
    for module_name, enabled in modules.items():
        if enabled and module_name in tool_templates:
            tool = tool_templates[module_name].copy()
            tool["annotations"] = {
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": False
            }
            tools.append(tool)
    
    return tools

def build_static_data_md(config):
    """构建静态数据文件（references/store_data.md）"""
    merchant = config["merchant"]
    stores = config.get("stores", [])
    recommendations = config.get("recommendations", [])
    
    lines = ["# {} - 静态数据\n".format(merchant["name"])]
    lines.append("> ⚠️ 以下为静态数据，如 MCP 不可用时作为兜底数据使用。\n")
    
    lines.append("## 商家信息\n")
    lines.append("- **名称**：{}".format(merchant["name"]))
    lines.append("- **城市**：{}".format(merchant["city"]))
    lines.append("- **行业**：{}".format(merchant["industry"]))
    lines.append("- **简介**：{}\n".format(merchant.get("description", "")))
    
    lines.append("## 门店信息\n")
    for store in stores:
        lines.append("### {}".format(store.get("name", merchant["name"])))
        lines.append("- **地址**：{}".format(store.get("address", "")))
        hours = store.get("hours", {})
        if hours:
            lines.append("- **营业时间**：{}（工作日）/ {}（周末）".format(
                hours.get("weekday", ""), hours.get("weekend", "")))
        if store.get("phone"):
            lines.append("- **电话**：{}".format(store["phone"]))
        lines.append("")
    
    lines.append("## 推荐服务/商品\n")
    for item in recommendations:
        tags = " / ".join(item.get("tags", []))
        lines.append("- **{}**：{} {}".format(item["name"], item.get("description", ""), tags))
    
    return "\n".join(lines)

def _copy_meituan_queue(output_dir):
    """复制美团排队相关文件到生成的 skill 目录"""
    src_queue = SKILL_DIR.parent / "jinguyuan-dumpling-skill" / "references" / "meituan-queue"
    dst_queue = output_dir / "references" / "meituan-queue"
    if src_queue.exists():
        import shutil
        shutil.copytree(src_queue, dst_queue, dirs_exist_ok=True)
        # 删除不必要的文件
        for pattern in ["**/__pycache__/**", "**/*.pyc"]:
            import glob
            for f in glob.glob(str(dst_queue / pattern), recursive=True):
                os.remove(f)

def generate_skill(config):
    """主生成函数"""
    merchant = config["merchant"]
    skill_name = to_skill_name(merchant["name"], merchant.get("language", "zh"))
    
    # 输出目录
    output_dir = Path.home() / "workspace" / "agent" / "skills" / skill_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    (output_dir / "references").mkdir(exist_ok=True)
    (output_dir / "scripts").mkdir(exist_ok=True)
    
    # 1. 生成 skill.json
    tools = generate_tools(config)
    skill_json = {
        "name": skill_name,
        "display_name": f"{merchant['name']}信息查询",
        "description": f"查询{merchant['name']}的门店地址、营业时间、{merchant['industry']}服务推荐、最新优惠活动等。",
        "version": "1.0.0",
        "author": merchant["name"],
        "license": "MIT",
        "category": "信息查询",
        "keywords": generate_keywords(merchant["name"], merchant["industry"], config.get("modules", {})),
        "brand_prompt": {
            "system_instruction": config.get("brand_instruction", f"你是{merchant['name']}的AI助手，用朴素、实在的方式回答问题。"),
            "tone": {
                "personality": config.get("tone_personality", "warm_and_honest"),
                "avoid": ["hype", "clickbait", "marketing_jargon"]
            }
        }
    }
    
    if config.get("mcp_config"):
        skill_json["mcp_server"] = config["mcp_config"]
    
    skill_json["tools"] = tools
    
    with open(output_dir / "skill.json", "w", encoding="utf-8") as f:
        json.dump(skill_json, f, ensure_ascii=False, indent=2)
    
    # 2. 生成 SKILL.md
    modules = config.get("modules", {})
    trigger_map = []
    
    if modules.get("store_info"):
        trigger_map.append(("门店在哪？营业时间？地址？", "get_store_info"))
    if modules.get("recommendations"):
        trigger_map.append(("有什么好吃的/推荐的服务？", "get_recommendations"))
    if modules.get("news"):
        trigger_map.append(("最近有什么活动/优惠？", "get_latest_news"))
    if modules.get("contact"):
        trigger_map.append(("怎么联系/电话多少？", "get_contact_info"))
    if modules.get("delivery"):
        trigger_map.append(("能送外卖吗？配送范围？", "get_delivery_info"))
    if modules.get("pickup"):
        trigger_map.append(("到店自取/提前下单", "get_pickup_link"))
    if modules.get("queue"):
        trigger_map.append(("排队/取号/等位", "get_queue_info + 内嵌排队Skill"))
    if modules.get("reservation"):
        trigger_map.append(("预约/预订服务", "get_reservation_info"))
    
    store_list_lines = ["## 门店信息\n"]
    for store in config.get("stores", []):
        store_list_lines.append(f"- **{store.get('name', merchant['name'])}**：{store.get('address', '')}")
    
    trigger_table = "\n".join([f"| \"{q}\" | `{t}` |" for q, t in trigger_map])
    
    brand_tone = config.get("tone_text", "用朴素、实在、有温度的方式回答问题。像朋友推荐常去的馆子，不堆营销话术。")
    
    # 读取模板
    template_path = REFERENCES_DIR / "skill_template.md"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        template = "# {name}\n\n配置生成失败，请检查模板文件。\n"
    
    # 简单替换
    mcp_config = config.get("mcp_config")
    is_mcp = mcp_config is not None and mcp_config.get("url")
    
    replacements = {
        "{{SKILL_NAME}}": skill_name,
        "{{MERCHANT_NAME}}": merchant["name"],
        "{{MERCHANT_DESCRIPTION}}": merchant.get("description", ""),
        "{{INDUSTRY}}": merchant["industry"],
        "{{TRIGGER_KEYWORDS}}": "、".join([merchant["name"], merchant["industry"]]),
        "{{STORE_LIST}}": "\n".join(store_list_lines),
        "{{CAPABILITIES_TABLE}}": "### 已开通能力\n" + "\n".join([f"- ✅ {m}" for m, v in modules.items() if v]),
        "{{TRIGGER_TABLE}}": trigger_table,
        "{{BRAND_TONE}}": brand_tone,
        "{{DEFAULT_PHONE}}": config.get("stores", [{}])[0].get("phone", "请到店咨询"),
        "{{SUPPORT_CONTACT}}": config.get("support_contact", "请联系商家管理员"),
    }
    # 排队信息
    queue_info = config.get("queue", {})
    if queue_info.get("description"):
        replacements["{{QUEUE_DESCRIPTION}}"] = f"**排队情况**：{queue_info['description']}\n\n> 💡 如果需要实时排队查询，商家可提供美团门店ID接入排队接口。"
    elif queue_info.get("has_queue"):
        replacements["{{QUEUE_DESCRIPTION}}"] = "**排队情况**：饭点/高峰期可能需要排队，建议提前电话咨询。"
    else:
        replacements["{{QUEUE_DESCRIPTION}}"] = "**排队情况**：目前暂无排队信息，随时可到店。建议致电确认。"
    
    # 门店ID映射（排队用）
    store_id_map = queue_info.get("store_ids", {})
    if store_id_map:
        lines = []
        for store_name, shop_id in store_id_map.items():
            lines.append(f"| {store_name} | `{shop_id}` |")
        replacements["{{STORE_ID_MAP}}"] = "\n".join(lines) if lines else "| （待配置） | （待配置） |"
    else:
        replacements["{{STORE_ID_MAP}}"] = "| （商家未提供美团门店ID） | （待配置） |"
    
    # 复制美团排队文件（如果需要排队）
    if queue_info.get("has_queue") and queue_info.get("store_ids"):
        _copy_meituan_queue(output_dir)
    if is_mcp:
        replacements["{{MCP_URL}}"] = mcp_config.get("url", "")
        replacements["{{MCP_AUTH}}"] = mcp_config.get("auth", "无认证")
    
    skill_md = template
    for placeholder, value in replacements.items():
        skill_md = skill_md.replace(placeholder, value)
    
    # 移除未解析的条件块
    if is_mcp:
        skill_md = re.sub(r'{{IF_NO_MCP}}.*?{{ENDIF_NO_MCP}}', '', skill_md, flags=re.DOTALL)
        skill_md = re.sub(r'{{IF_MCP}}(.*?){{ENDIF}}', r'\1', skill_md, flags=re.DOTALL)
    else:
        skill_md = re.sub(r'{{IF_MCP}}.*?{{ENDIF}}', '', skill_md, flags=re.DOTALL)
        skill_md = re.sub(r'{{IF_NO_MCP}}(.*?){{ENDIF_NO_MCP}}', r'\1', skill_md, flags=re.DOTALL)
    skill_md = re.sub(r'{{IF_NO_MCP}}.*?{{ENDIF_NO_MCP}}', '', skill_md, flags=re.DOTALL)
    
    with open(output_dir / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(skill_md)
    
    # 3. 生成静态数据
    static_data = build_static_data_md(config)
    with open(output_dir / "references" / "store_data.md", "w", encoding="utf-8") as f:
        f.write(static_data)
    
    return str(output_dir), skill_name

def main():
    parser = argparse.ArgumentParser(description="商家技能生成器")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--config", help="商家配置JSON字符串")
    group.add_argument("--config-file", help="商家配置文件路径")
    parser.add_argument("--output-dir", help="输出目录（可选）")
    args = parser.parse_args()
    
    # 读取配置
    if args.config:
        config = json.loads(args.config)
    elif args.config_file:
        with open(args.config_file, encoding="utf-8") as f:
            config = json.load(f)
    else:
        print("❌ 请提供 --config 或 --config-file 参数")
        print("参考格式：python3 generate_skill.py --config '{\"merchant\":{\"name\":\"测试商家\",\"city\":\"北京\",\"industry\":\"餐饮\"}}'")
        sys.exit(1)
    
    # 生成
    output_path, skill_name = generate_skill(config)
    
    print(f"✅ 技能生成成功！")
    print(f"📁 生成路径：{output_path}")
    print(f"🏷️  技能名称：{skill_name}")
    queue_info = config.get("queue", {})
    if queue_info.get("has_queue") and queue_info.get("store_ids"):
        store_ids = queue_info.get("store_ids", {})
        print(f"\n🔧 美团排队配置（已内置，需首次授权）：")
        for store_name, shop_id in store_ids.items():
            print(f"  · {store_name}：门店ID = {shop_id}")
        print(f"\n  首次使用需扫码授权：")
        print(f"  1. 运行：pt-passport auth get-code --client_id 170f5f2dbbde4048bd4a5e4ed28209cc")
        print(f"  2. 用美团App扫码授权")
        print(f"  3. 完成！")
    print(f"\n打包命令：")
    print(f"  bash {SKILL_DIR}/scripts/package_skill.sh {skill_name}")
    print(f"\n安装命令：")
    print(f"  clawhub install {skill_name}")

if __name__ == "__main__":
    main()
