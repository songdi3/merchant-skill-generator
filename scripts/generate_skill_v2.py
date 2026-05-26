#!/usr/bin/env python3
"""
商家技能生成器 v2.0 - 核心生成脚本

目标：生成和金谷园一样完整的商家 AI 技能
- 9+ 工具函数，覆盖顾客所有场景
- 行业专属工具（餐饮/健身/美容/零售/医疗）
- 自动从服务清单生成对应工具

用法:
    python3 generate_skill.py --config-file <配置文件路径>
"""

import json
import os
import re
import sys
import shutil
import argparse
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent

# ============================================================================
# 工具函数模板库（按行业分类）
# ============================================================================

# 通用工具（所有商家都需要）
BASE_TOOLS = {
    "store_info": {
        "name": "get_store_info",
        "display_name": "门店信息",
        "description": "查询{mName}的门店地址、营业时间、联系电话、交通指引等基本信息。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问地址/在哪/怎么去/几点开门/营业时间"
    },
    "recommendations": {
        "name": "get_recommendations",
        "display_name": "推荐服务/商品",
        "description": "获取{mName}当前的推荐服务或商品列表，含招牌/热门/新品等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问有什么好吃/推荐/招牌/新品/点什么"
    },
    "contact": {
        "name": "get_contact_info",
        "display_name": "联系方式",
        "description": "获取{mName}的联系电话、微信公众号、官方账号等联系方式。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问电话/微信/怎么联系"
    },
    "news": {
        "name": "get_latest_news",
        "display_name": "最新动态/公告",
        "description": "获取{mName}的最新优惠活动、门店通知、重要公告等动态信息。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问有什么优惠/最近活动/通知/公告"
    },
}

# 餐饮行业工具
RESTAURANT_TOOLS = {
    "delivery": {
        "name": "get_delivery_info",
        "display_name": "外卖配送",
        "description": "获取{mName}外卖配送信息，包括配送平台、范围、起送价、配送时间等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问能外卖吗/怎么点外卖/配送范围/起送价"
    },
    "pickup": {
        "name": "get_pickup_link",
        "display_name": "到店自取",
        "description": "获取{mName}小程序/公众号到店自取下单链接，用户可提前下单到店取餐。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户想到店自取/外带/提前点餐/小程序下单"
    },
    "menu": {
        "name": "get_menu",
        "display_name": "菜单/价格",
        "description": "获取{mName}完整菜单和价格表，用户可查询具体菜品价格。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问菜单/价格/某道菜多少钱/有特价菜吗"
    },
    "queue": {
        "name": "get_queue_info",
        "display_name": "排队取号",
        "description": "获取{mName}堂食排队取号方式和当前排队状态，支持在线取号。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问排队/取号/等位/需要等多久"
    },
    "reservation": {
        "name": "get_reservation_info",
        "display_name": "座位/包间预订",
        "description": "获取{mName}座位预订或包间预订信息，包括预订方式和可预订座位类型。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问预订座位/包间/可以预约吗"
    },
    "recipes": {
        "name": "get_recipes",
        "display_name": "菜品配方",
        "description": "查询{mName}公开的菜品配方和做法，用户感兴趣时可介绍。",
        "inputSchema": {"type": "object", "properties": {"recipe_id": {"type": "string", "description": "配方ID，不传则返回所有配方"}}, "required": []},
        "scenario": "用户问某道菜怎么做/配方/是怎么做的"
    },
    "wifi": {
        "name": "get_wifi_info",
        "display_name": "店内Wi-Fi",
        "description": "获取{mName}店内Wi-Fi名称和密码，用户在店连接网络时使用。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问Wi-Fi/密码/无线网/上网"
    },
    "packaging": {
        "name": "get_packaging_info",
        "display_name": "生鲜打包/外带",
        "description": "获取{mName}生鲜打包、外带服务信息，包括如何购买、 保存方法、烹饪建议等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问能打包吗/带走/生鲜打包/买回去怎么煮"
    },
    "membership": {
        "name": "get_membership_info",
        "display_name": "会员/优惠",
        "description": "获取{mName}会员权益、优惠券、会员日活动等优惠信息。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问会员/优惠/优惠券/打折/折扣"
    },
}

# 健身/运动行业工具
FITNESS_TOOLS = {
    "courses": {
        "name": "get_courses",
        "display_name": "课程/团课",
        "description": "获取{mName}当前开设的课程/团课列表，包括课程类型、时间、教练等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问有什么课/团课/课程表/什么时候有课"
    },
    "coaches": {
        "name": "get_coaches",
        "display_name": "教练介绍",
        "description": "获取{mName}教练团队介绍，包括教练资质、擅长领域、教授课程等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问教练/教练介绍/哪个教练好/私教"
    },
    "membership": {
        "name": "get_membership_info",
        "display_name": "会员卡/套餐",
        "description": "获取{mName}会员卡类型、价格、权益、套餐组合等会员信息。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问会员卡/价格/套餐/年卡/月卡/多少钱"
    },
    "booking": {
        "name": "get_booking_info",
        "display_name": "预约课程/私教",
        "description": "获取{mName}预约课程或私教的方式，包括预约规则、可预约时间等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问怎么预约/可以预约吗/预约课程/预约私教"
    },
    "assessment": {
        "name": "get_assessment_info",
        "display_name": "体测/评估",
        "description": "获取{mName}体测或身体评估服务的信息，包括流程、预约方式等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问体测/身体评估/体脂检测/检测"
    },
    "queue": {
        "name": "get_queue_info",
        "display_name": "排队/等位",
        "description": "获取{mName}高峰时段排队等位情况，热门时段可能需要等位。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问排队/等位/人多吗/需要等多久"
    },
}

# 美发/美容行业工具
BEAUTY_TOOLS = {
    "services": {
        "name": "get_services",
        "display_name": "服务项目/价格",
        "description": "获取{mName}服务项目列表和价格，包括洗发、剪发、烫染、美容等各项服务价格。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问价格/多少钱/洗头多少钱/烫发价格"
    },
    "stylists": {
        "name": "get_stylists",
        "display_name": "设计师/美容师",
        "description": "获取{mName}设计师或美容师团队介绍，包括擅长风格、工作年限等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问设计师/美容师/哪个好/推荐"
    },
    "booking": {
        "name": "get_booking_info",
        "display_name": "预约服务",
        "description": "获取{mName}在线预约服务的方式和可预约时间段。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问怎么预约/可以预约吗/预约时间"
    },
    "membership": {
        "name": "get_membership_info",
        "display_name": "会员卡/套餐",
        "description": "获取{mName}会员卡、套餐、会员权益等信息。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问会员卡/套餐/打折/折扣"
    },
    "queue": {
        "name": "get_queue_info",
        "display_name": "排队等位",
        "description": "获取{mName}排队等位情况，高峰时段可能需要等位。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问排队/等位/人多吗/需要等多久"
    },
    "gallery": {
        "name": "get_gallery",
        "display_name": "作品展示",
        "description": "获取{mName}客户作品展示，包括发型前后对比、风格展示等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户看效果/作品/前后对比/案例"
    },
}

# 零售/便利店行业工具
RETAIL_TOOLS = {
    "products": {
        "name": "get_products",
        "display_name": "商品查询",
        "description": "获取{mName}商品列表，包括热销商品、新品上架、特价商品等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问有什么商品/有XX吗/新品/热销"
    },
    "inventory": {
        "name": "get_inventory",
        "display_name": "库存查询",
        "description": "查询{mName}特定商品是否有货，支持商品名或品类查询。",
        "inputSchema": {"type": "object", "properties": {"query": {"type": "string", "description": "商品名称或品类"}}, "required": ["query"]},
        "scenario": "用户问有XX吗/XX有货吗/还有吗"
    },
    "promotions": {
        "name": "get_promotions",
        "display_name": "促销/特价",
        "description": "获取{mName}当前促销活动、特价商品、优惠券等信息。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问有什么优惠/特价/打折/促销/优惠券"
    },
    "delivery": {
        "name": "get_delivery_info",
        "display_name": "配送服务",
        "description": "获取{mName}配送服务信息，包括配送范围、费用、配送时间等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问能送吗/配送/怎么送货"
    },
}

# 医疗/健康行业工具
MEDICAL_TOOLS = {
    "departments": {
        "name": "get_departments",
        "display_name": "科室/服务介绍",
        "description": "获取{mName}科室设置、专科服务、擅长领域等介绍。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问有什么科/科室/看什么病/擅长什么"
    },
    "doctors": {
        "name": "get_doctors",
        "display_name": "医生介绍",
        "description": "获取{mName}医生团队介绍，包括出诊时间、擅长领域、职称等。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问医生/专家/出诊时间/挂号"
    },
    "booking": {
        "name": "get_booking_info",
        "display_name": "预约挂号",
        "description": "获取{mName}在线预约挂号的方式、可预约时间和注意事项。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问怎么挂号/可以预约吗/网上预约"
    },
    "queue": {
        "name": "get_queue_info",
        "display_name": "排队叫号",
        "description": "获取{mName}当前排队叫号状态，用户可了解等待时间。",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "scenario": "用户问排队/叫号/等多久/现在排到几号了"
    },
}

# 行业→工具映射
INDUSTRY_TOOLS = {
    "餐饮": RESTAURANT_TOOLS,
    "餐厅": RESTAURANT_TOOLS,
    "饺子馆": RESTAURANT_TOOLS,
    "火锅": RESTAURANT_TOOLS,
    "烧烤": RESTAURANT_TOOLS,
    "奶茶": RESTAURANT_TOOLS,
    "咖啡": RESTAURANT_TOOLS,
    "烘焙": RESTAURANT_TOOLS,
    "快餐": RESTAURANT_TOOLS,
    "健身": FITNESS_TOOLS,
    "瑜伽": FITNESS_TOOLS,
    "游泳": FITNESS_TOOLS,
    "运动": FITNESS_TOOLS,
    "美容": BEAUTY_TOOLS,
    "美发": BEAUTY_TOOLS,
    "美甲": BEAUTY_TOOLS,
    "按摩": BEAUTY_TOOLS,
    "SPA": BEAUTY_TOOLS,
    "零售": RETAIL_TOOLS,
    "便利店": RETAIL_TOOLS,
    "超市": RETAIL_TOOLS,
    "药店": RETAIL_TOOLS,
    "医疗": MEDICAL_TOOLS,
    "医院": MEDICAL_TOOLS,
    "诊所": MEDICAL_TOOLS,
    "口腔": MEDICAL_TOOLS,
    "眼科": MEDICAL_TOOLS,
}

def to_skill_name(merchant_name, language="zh"):
    """将商家名称转换为 skill 名称"""
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
        '餐':'can','厅':'ting','炸':'zha','酱':'jiang','面':'mian',
        '老':'lao','王':'wang','北':'bei','京':'jing','上':'shang','海':'hai',
        '烤':'kao','匠':'jiang','麻':'ma','辣':'la','鱼':'yu','西':'xi','直':'zhi','门':'men',
        '有':'you','礼':'li','面':'mian','知':'zhi','春':'chun','路':'lu',
        '置':'zhi','顶':'ding','龙':'long','域':'yu','霍':'huo','营':'ying',
        '烧':'shao','肉':'rou','牛':'niu','羊':'yang','猪':'zhu','鸡':'ji','鸭':'ya',
        '火':'huo','锅':'guo','串':'chuan','卤':'lu','面':'mian','米':'mi','粉':'fen',
        '粥':'zhou','馒':'man','头':'tou','包':'bao','子':'zi',
    }
    result = []
    for char in merchant_name:
        if '\u4e00' <= char <= '\u9fff':
            result.append(pinyin_map.get(char, ''))
        elif char.isalnum():
            result.append(char.lower())
    name = '-'.join([r for r in result if r])
    name = re.sub(r'-+', '-', name).strip('-').lower()
    return name

def generate_tools_v2(config):
    """根据配置生成所有适用的工具函数"""
    mname = config["merchant"]["name"]
    industry = config["merchant"].get("industry", "")
    enabled_services = config.get("services", {})
    
    tools = []
    seen_names = set()
    
    # 始终添加基础工具
    for key, tpl in BASE_TOOLS.items():
        if enabled_services.get(key, True):  # 默认启用
            tool = {
                "name": tpl["name"],
                "display_name": tpl["display_name"],
                "description": tpl["description"].format(mName=mname),
                "inputSchema": tpl["inputSchema"],
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False
                }
            }
            if tool["name"] not in seen_names:
                tools.append(tool)
                seen_names.add(tool["name"])
    
    # 添加行业专属工具
    for ind_key, ind_tools in INDUSTRY_TOOLS.items():
        if ind_key in industry or any(k in industry for k in [ind_key]):
            for key, tpl in ind_tools.items():
                if enabled_services.get(key, False):  # 行业工具默认关闭，由services控制
                    tool = {
                        "name": tpl["name"],
                        "display_name": tpl["display_name"],
                        "description": tpl["description"].format(mName=mname),
                        "inputSchema": tpl["inputSchema"],
                        "annotations": {
                            "readOnlyHint": True,
                            "destructiveHint": False,
                            "idempotentHint": True,
                            "openWorldHint": False
                        }
                    }
                    if tool["name"] not in seen_names:
                        tools.append(tool)
                        seen_names.add(tool["name"])
    
    return tools

def generate_tools(config):
    """兼容旧版：生成 tools 数组（v1格式）"""
    modules = config.get("modules", {})
    mname = config["merchant"]["name"]
    
    templates = {
        "store_info": {
            "name": "get_store_info",
            "display_name": "门店信息",
            "description": f"查询{mname}的门店地址、营业时间、联系电话等信息。"
        },
        "recommendations": {
            "name": "get_recommendations",
            "display_name": "推荐服务",
            "description": f"获取{mname}当前推荐的服务/商品列表。"
        },
        "news": {
            "name": "get_latest_news",
            "display_name": "最新公告",
            "description": f"获取{mname}的最新优惠活动和门店通知。"
        },
        "contact": {
            "name": "get_contact_info",
            "display_name": "联系方式",
            "description": f"获取{mname}的联系电话、微信公众号等联系方式。"
        },
        "delivery": {
            "name": "get_delivery_info",
            "display_name": "外卖配送",
            "description": f"获取{mname}的外卖配送范围、起送价等信息。"
        },
        "pickup": {
            "name": "get_pickup_link",
            "display_name": "到店自取",
            "description": f"获取{mname}小程序到店自取下单链接。"
        },
        "queue": {
            "name": "get_queue_info",
            "display_name": "排队取号",
            "description": f"获取{mname}堂食排队取号方式和当前排队状态。"
        },
        "reservation": {
            "name": "get_reservation_info",
            "display_name": "服务预约",
            "description": f"获取{mname}的在线预约方式和可预约服务项目。"
        },
    }
    
    tools = []
    for key, enabled in modules.items():
        if enabled and key in templates:
            tool = templates[key].copy()
            tool["inputSchema"] = {"type": "object", "properties": {}, "required": []}
            tool["annotations"] = {
                "readOnlyHint": True, "destructiveHint": False,
                "idempotentHint": True, "openWorldHint": False
            }
            tools.append(tool)
    
    return tools

def build_skill_md_v2(config, tools):
    """生成完整 SKILL.md（v2格式，覆盖所有服务）"""
    mname = config["merchant"]["name"]
    industry = config["merchant"].get("industry", "")
    desc = config["merchant"].get("description", "")
    stores = config.get("stores", [])
    recommendations = config.get("recommendations", [])
    services = config.get("services", {})
    tone = config.get("tone", "朴素实在")
    mcp_url = config.get("mcp_url")
    queue_info = config.get("queue", {})
    miniprogram = config.get("miniprogram", {})
    
    lines = []
    lines.append("---")
    lines.append(f"name: {to_skill_name(mname)}")
    
    # description：包含所有启用的服务
    caps = []
    for t in tools:
        if t["name"] == "get_store_info": caps.append("门店信息查询")
        elif t["name"] == "get_recommendations": caps.append("推荐服务/商品")
        elif t["name"] == "get_news" or t["name"] == "get_latest_news": caps.append("最新动态")
        elif t["name"] == "get_contact_info": caps.append("联系方式")
        elif t["name"] == "get_delivery_info": caps.append("外卖配送咨询")
        elif t["name"] == "get_pickup_link": caps.append("到店自取下单")
        elif t["name"] == "get_menu": caps.append("菜单/价格查询")
        elif t["name"] == "get_queue_info": caps.append("排队取号")
        elif t["name"] == "get_reservation_info": caps.append("座位/服务预约")
        elif t["name"] == "get_wifi_info": caps.append("店内Wi-Fi")
        elif t["name"] == "get_recipes": caps.append("菜品配方")
        elif t["name"] == "get_packaging_info": caps.append("生鲜打包外带")
        elif t["name"] == "get_membership_info": caps.append("会员优惠")
        elif t["name"] == "get_courses": caps.append("课程团课")
        elif t["name"] == "get_coaches": caps.append("教练介绍")
        elif t["name"] == "get_booking_info": caps.append("预约服务")
        elif t["name"] == "get_assessment_info": caps.append("体测评估")
        elif t["name"] == "get_services": caps.append("服务项目价格")
        elif t["name"] == "get_stylists": caps.append("设计师美容师")
        elif t["name"] == "get_gallery": caps.append("作品展示")
        elif t["name"] == "get_products": caps.append("商品查询")
        elif t["name"] == "get_inventory": caps.append("库存查询")
        elif t["name"] == "get_promotions": caps.append("促销特价")
        elif t["name"] == "get_departments": caps.append("科室服务")
        elif t["name"] == "get_doctors": caps.append("医生介绍")
    
    caps_str = "、".join(caps) if caps else "基础信息查询"
    lines.append(f"description: {mname}{caps_str}。触发词：{mname}、{industry}。")
    lines.append("version: 1.0.0")
    lines.append("alwaysApply: false")
    lines.append("keywords:")
    for kw in [mname, industry] + list(mname):
        lines.append(f"  - {kw}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {mname} · AI 助手")
    lines.append("")
    lines.append("## 商家简介")
    lines.append(desc)
    lines.append("")
    
    # 门店信息
    if stores:
        lines.append("## 门店信息")
        for store in stores:
            lines.append(f"### {store.get('name', mname)}")
            lines.append(f"- 📍 {store.get('address', '')}")
            if store.get('phone'):
                lines.append(f"- 📞 {store['phone']}")
            hours = store.get('hours', {})
            if hours:
                hours_str = hours.get('weekday', '') or hours.get('full', ''))
                lines.append(f"- 🕐 {hours_str}")
            lines.append("")
    
    # 招牌推荐
    if recommendations:
        lines.append("## 招牌推荐")
        lines.append("")
        lines.append("| 项目 | 说明 |")
        lines.append("|------|------|")
        for r in recommendations:
            tags = "/".join(r.get('tags', []))
            lines.append(f"| {r['name']} | {r.get('description', '')} {tags} |")
        lines.append("")
    
    # 各工具的详细章节
    for tool in tools:
        if tool["name"] == "get_delivery_info":
            lines.append("## 外卖配送")
            lines.append(f"支持外卖平台下单，配送范围约3公里。")
            lines.append("")
        elif tool["name"] == "get_pickup_link":
            lines.append("## 到店自取")
            if miniprogram.get('name'):
                lines.append(f"可使用「{miniprogram['name']}」小程序提前下单，到店直接取餐。")
            lines.append("")
        elif tool["name"] == "get_menu":
            lines.append("## 菜单/价格")
            lines.append("如有具体菜单需求，请致电门店或到店查看。")
            lines.append("")
        elif tool["name"] == "get_wifi_info":
            lines.append("## 店内Wi-Fi")
            lines.append("到店后询问店员Wi-Fi密码。")
            lines.append("")
        elif tool["name"] == "get_membership_info":
            lines.append("## 会员/优惠")
            lines.append("到店或致电门店了解会员权益和当前优惠活动。")
            lines.append("")
        elif tool["name"] == "get_recipes":
            lines.append("## 菜品配方")
            lines.append("部分菜品配方公开，感兴趣可向店员咨询。")
            lines.append("")
        elif tool["name"] == "get_courses":
            lines.append("## 课程/团课")
            lines.append("最新课程安排请致电门店或关注官方公众号。")
            lines.append("")
    
    # 排队信息
    if any(t["name"] == "get_queue_info" for t in tools):
        qdesc = queue_info.get("description", "饭点/高峰期可能需要排队，建议提前电话咨询。")
        lines.append("## 排队情况")
        lines.append(qdesc)
        if queue_info.get("store_ids"):
            lines.append("")
            lines.append("**美团门店ID**：")
            for sname, sid in queue_info["store_ids"].items():
                lines.append(f"- {sname}：`{sid}`")
        lines.append("")
    
    # MCP信息
    if mcp_url:
        lines.append("## MCP 实时接口")
        lines.append(f"本技能通过 MCP 协议实时获取数据。")
        lines.append(f"- **MCP 端点**：`{mcp_url}`")
        lines.append("")
    
    # 品牌调性
    lines.append("## 品牌调性")
    lines.append(f"AI 助手风格：**{tone}**。像朋友推荐常去的店，不夸张，不套话，不知道就说不知道。")
    lines.append("")
    
    # 触发场景
    lines.append("## 常见问题与工具映射")
    lines.append("")
    lines.append("| 用户问 | 调用工具 |")
    lines.append("|--------|---------|")
    for tool in tools:
        scenario = _get_tool_scenario(tool["name"], services)
        if scenario:
            lines.append(f"| {scenario} | `{tool['name']}` |")
    lines.append("")
    
    # 盲区应对
    lines.append("## 盲区应对")
    lines.append("")
    lines.append("超出工具覆盖范围的问题（如具体价格、库存细节等）：")
    lines.append("1. **诚实承认**——不装不编")
    lines.append("2. **递上已有信息**——地址、营业时间等")
    lines.append("3. **指一条明路**——到店咨询或致电门店")
    lines.append("")
    default_phone = stores[0].get('phone', '') if stores else ''
    lines.append(f"> 示例：「这个我没查到，怕说错了耽误您。您直接打 {default_phone} 问店员最准。」")
    
    return "\n".join(lines)

def _get_tool_scenario(tool_name, services):
    """获取工具对应的用户问法"""
    scenarios = {
        "get_store_info": "门店在哪/几点开门/地址/怎么去",
        "get_recommendations": "有什么好吃/推荐/招牌/点什么",
        "get_contact_info": "电话/微信/怎么联系",
        "get_latest_news": "最新优惠/活动/通知/公告",
        "get_delivery_info": "能外卖吗/怎么点/配送范围",
        "get_pickup_link": "到店自取/外带/提前点餐",
        "get_menu": "菜单/价格/某道菜多少钱",
        "get_queue_info": "排队/取号/等位/需要等多久",
        "get_reservation_info": "预订座位/包间/可以预约吗",
        "get_wifi_info": "Wi-Fi/密码/无线网/上网",
        "get_recipes": "怎么做/配方/是怎么做的",
        "get_packaging_info": "打包/带走/生鲜打包/怎么煮",
        "get_membership_info": "会员/优惠/优惠券/打折",
        "get_courses": "有什么课/课程表/什么时候有课",
        "get_coaches": "教练/私教/哪个教练好",
        "get_booking_info": "怎么预约/预约课程/预约私教",
        "get_assessment_info": "体测/身体评估/体脂检测",
        "get_services": "价格/多少钱/洗头/烫发价格",
        "get_stylists": "设计师/美容师/哪个好",
        "get_gallery": "作品/效果/前后对比/案例",
        "get_products": "有什么商品/有XX吗/新品",
        "get_inventory": "有货吗/还有吗/XX在哪",
        "get_promotions": "优惠/特价/打折/促销",
        "get_departments": "有什么科/科室/看什么病",
        "get_doctors": "医生/专家/出诊时间/挂号",
    }
    return scenarios.get(tool_name, "")

def build_skill_json_v2(config, tools):
    """生成完整 skill.json（v2格式）"""
    mname = config["merchant"]["name"]
    skill_name = to_skill_name(mname)
    
    tone_map = {
        "朴素实在": "warm_and_honest",
        "活泼亲切": "friendly_playful",
        "专业严谨": "professional_formal",
        "温柔体贴": "gentle_caring",
    }
    
    brand_instruction = config.get("brand_instruction", f"你是{mname}的AI助手。品牌调性：{config.get('tone', '朴素实在')}。像老朋友推荐常去的店，不夸张，不套话，不知道就说不知道，切勿编造数据。")
    
    skill_json = {
        "name": skill_name,
        "display_name": f"{mname} AI助手",
        "description": f"{mname}信息查询与在线服务助手。",
        "version": "1.0.0",
        "author": mname,
        "license": "MIT",
        "category": config["merchant"].get("industry", "生活服务"),
        "keywords": [mname, config["merchant"].get("industry", "")],
        "brand_prompt": {
            "system_instruction": brand_instruction,
            "tone": {
                "personality": tone_map.get(config.get("tone", ""), "warm_and_honest"),
                "avoid": ["hype", "clickbait", "marketing_jargon"]
            }
        },
        "tools": tools
    }
    
    # MCP配置
    if config.get("mcp_url"):
        skill_json["mcp_server"] = {
            "transport": "streamable-http",
            "url": config["mcp_url"]
        }
    
    return skill_json

def build_static_data_md(config):
    """构建静态数据文件"""
    mname = config["merchant"]["name"]
    stores = config.get("stores", [])
    recs = config.get("recommendations", [])
    
    lines = [f"# {mname} - 静态数据\n"]
    lines.append("> ⚠️ 以下为静态数据，MCP不可用时作为兜底数据使用。\n")
    lines.append(f"## 商家简介\n")
    lines.append(f"{config['merchant'].get('description', '')}\n")
    
    if stores:
        lines.append("## 门店信息\n")
        for store in stores:
            lines.append(f"### {store.get('name', mname)}\n")
            lines.append(f"- 地址：{store.get('address', '')}\n")
            if store.get('phone'):
                lines.append(f"- 电话：{store['phone']}\n")
            hours = store.get('hours', {})
            if hours:
                lines.append(f"- 营业时间：{hours.get('weekday', '')}\n")
            lines.append("\n")
    
    if recs:
        lines.append("## 招牌推荐\n")
        for r in recs:
            lines.append(f"- **{r['name']}**：{r.get('description', '')}\n")
    
    return "".join(lines)

def _copy_meituan_queue(output_dir):
    """复制美团排队文件"""
    src = SKILL_DIR.parent / "jinguyuan-dumpling-skill" / "references" / "meituan-queue"
    dst = output_dir / "references" / "meituan-queue"
    if src.exists():
        import shutil
        shutil.copytree(src, dst, dirs_exist_ok=True)
        # 清理缓存
        for root, dirs, files in os.walk(dst):
            for d in dirs[:]:
                if d == "__pycache__":
                    shutil.rmtree(os.path.join(root, d))
                    dirs.remove(d)
            for f in files:
                if f.endswith(".pyc"):
                    os.remove(os.path.join(root, f))

def generate_skill(config):
    """主生成函数"""
    mname = config["merchant"]["name"]
    skill_name = to_skill_name(mname)
    output_dir = Path.home() / "workspace" / "agent" / "skills" / skill_name
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "references").mkdir(exist_ok=True)
    (output_dir / "scripts").mkdir(exist_ok=True)
    
    # 生成工具函数
    tools = generate_tools_v2(config)
    
    # 生成 SKILL.md
    skill_md = build_skill_md_v2(config, tools)
    with open(output_dir / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(skill_md)
    
    # 生成 skill.json
    skill_json = build_skill_json_v2(config, tools)
    with open(output_dir / "skill.json", "w", encoding="utf-8") as f:
        json.dump(skill_json, f, ensure_ascii=False, indent=2)
    
    # 生成静态数据
    static_data = build_static_data_md(config)
    with open(output_dir / "references" / "store_data.md", "w", encoding="utf-8") as f:
        f.write(static_data)
    
    # 复制美团排队文件（如需要）
    queue_info = config.get("queue", {})
    if queue_info.get("has_queue") and queue_info.get("store_ids"):
        _copy_meituan_queue(output_dir)
    
    return str(output_dir), skill_name, len(tools)

def main():
    parser = argparse.ArgumentParser(description="商家技能生成器 v2.0")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--config", help="商家配置JSON字符串")
    group.add_argument("--config-file", help="商家配置文件路径")
    args = parser.parse_args()
    
    if args.config:
        config = json.loads(args.config)
    elif args.config_file:
        with open(args.config_file, encoding="utf-8") as f:
            config = json.load(f)
    else:
        print("❌ 请提供 --config 或 --config-file 参数")
        sys.exit(1)
    
    output_path, skill_name, tool_count = generate_skill(config)
    
    print(f"✅ 技能生成成功！")
    print(f"📁 生成路径：{output_path}")
    print(f"🏷️  技能名称：{skill_name}")
    print(f"🔧 工具函数：{tool_count} 个")
    print(f"\n打包命令：")
    print(f"  bash {SKILL_DIR}/scripts/package_skill.sh {skill_name}")
    print(f"\n安装命令：")
    print(f"  clawhub install {skill_name}")

if __name__ == "__main__":
    main()
