#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自用全能签软件源清单生成器（支持蓝奏云 / 本地直链双模式）

两种模式：
  模式 A - 蓝奏云：在下面 APPS 列表里手填应用名 + 蓝奏分享链接，IPA 不用上传
  模式 B - 本地直链：把 IPA / dylib 放进 ipa/ 目录，脚本自动扫描生成

用法：
  1. 修改下面【配置区】和【应用列表】
  2. 运行：python3 gen_appstore.py
  3. 生成 appstore.json，上传到 GitHub Pages / 其他托管
"""

import os
import json
import datetime

# ==================== 配置区（改成你的） ====================
# 托管后 appstore.json 所在的 https 根地址，结尾不要加斜杠
BASE_URL = "https://xiaoyun1995314.github.io/my-source"

# 源信息
SOURCE_NAME = "訫云科技
自用源，请勿传播"
SOURCE_ICON = "https://xiaoyun1995314.github.io/my-source/icons/123.png.PNG"                                # 源图标 https 地址，没有留空
TINT_COLOR = "018084"                           # 主题色

# ---------- 应用列表（蓝奏云模式，在这里逐条加应用） ----------
# lanzou=True  → downloadURL 是蓝奏云分享链接，isLanZouCloud=1
# lanzou=False → downloadURL 是普通 https 直链，isLanZouCloud=0
# iconURL 没有就留空 ""
APPS = [
    {
        "name": "应用一",
        "type": "4",            # 4=IPA 应用，5=dylib 动态库
        "version": "1.0.0",
        "versionDescription": "自用说明",
        "lanzou": True,
        "downloadURL": "https://wwbli.lanzouq.com/irH6j4grxf6h",  # 蓝奏分享地址，不带 &pwd
        "pwd": "fceb",          # 蓝奏提取码；无密码就留空 ""
        "iconURL": "",
    },
    # 复制这一段，继续加应用：
    # {
    #     "name": "应用二",
    #     "type": "4",
    #     "version": "2.0.0",
    #     "versionDescription": "自用说明",
    #     "lanzou": False,
    #     "downloadURL": "https://你的直链/app2.ipa",
    #     "iconURL": "",
    # },
]
# ==========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(SCRIPT_DIR, "appstore.json")


def iso_now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def build_app(item: dict) -> dict:
    """把一条应用配置转成全能签清单条目"""
    is_lanzou = "1" if item.get("lanzou", False) else "0"
    url = item["downloadURL"]
    # 蓝奏云带密码：地址 &pwd=提取码；无密码则保持原链接
    if item.get("lanzou", False) and item.get("pwd"):
        sep = "&" if "?" in url else "&"
        url = f"{url}{sep}pwd={item['pwd']}"
    return {
        "name": item["name"],
        "type": item.get("type", "4"),
        "version": item.get("version", "1.0.0"),
        "versionDate": iso_now(),
        "versionDescription": item.get("versionDescription", "自用"),
        "lock": "0",
        "downloadURL": url,
        "isLanZouCloud": is_lanzou,
        "iconURL": item.get("iconURL", ""),
        "tintColor": TINT_COLOR,
        "size": 0,
    }


def main():
    apps = [build_app(item) for item in APPS]

    manifest = {
        "identifier": SOURCE_NAME,
        "sourceURL": f"{BASE_URL}/appstore.json",
        "sourceicon": SOURCE_ICON,
        "unlockURL": f"{BASE_URL}/appstore.json",
        "apps": apps,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"[完成] 已生成 {OUT_FILE}")
    print(f"[收录] {len(apps)} 个包：")
    for a in apps:
        cloud = "蓝奏云" if a["isLanZouCloud"] == "1" else "直链"
        print(f"  - {a['name']} ({cloud}, v{a['version']})")
    print(f"\n[下一步] 把 appstore.json 上传到托管，")
    print(f"         全能签添加源：{BASE_URL}/appstore.json")


if __name__ == "__main__":
    main()
