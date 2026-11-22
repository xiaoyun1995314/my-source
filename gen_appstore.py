#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
訫云软件源 · appstore.json 生成脚本（GitHub Pages）
用法：
  1. 把 .ipa 文件放进 ipas/ 目录
  2. （可选）在下方 LANZOU_MAP 里填蓝奏云直链
  3. python3 gen_appstore.py
  4. 提交到 GitHub，GitHub Pages 自动生效
源地址：https://xiaoyun1995314.github.io/my-source/appstore.json
"""

import os
import json
import plistlib
import zipfile
import shutil
import datetime
import re

# ===================== 源信息配置（改这里） =====================
SOURCE_NAME = "訫云软件源"
# GitHub Pages：仓库名 my-source，文件放仓库根目录
SOURCE_URL = "https://xiaoyun1995314.github.io/my-source/appstore.json"
SOURCE_IDENTIFIER = "cn.xiaoyun.source"
SUBTITLE = "訫云软件源 · 个人侧载源"
DESCRIPTION = "訫云软件源，仅供个人技术学习使用"
DEVELOPER_NAME = "訫云"
WEBSITE = "https://xiaoyun1995314.github.io/my-source/"

# 本地目录（相对本脚本）
IPA_DIR = "ipas"
ICON_DIR = "icons"
OUTPUT_FILE = "appstore.json"

# 蓝奏云直链映射：文件名 -> 直链。留空则用 GitHub Pages 相对地址托管 IPA
# 示例：LANZOU_MAP = {"微信.ipa": "https://xxx.lanzou.com/xxx"}
LANZOU_MAP = {}

# ===================== 以下一般不用改 =====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def resolve(path):
    return os.path.join(BASE_DIR, path)


def read_info_plist(ipa_path):
    """从 IPA 里读取 Info.plist（兼容二进制/XML）"""
    with zipfile.ZipFile(ipa_path, "r") as zf:
        plist_name = None
        for name in zf.namelist():
            if re.match(r"Payload/[^/]+/Info\.plist$", name):
                plist_name = name
                break
        if not plist_name:
            return {}
        with zf.open(plist_name) as f:
            return plistlib.load(f)


def extract_icon(ipa_path, out_dir):
    """从 IPA 提取 AppIcon，返回图标文件名"""
    with zipfile.ZipFile(ipa_path, "r") as zf:
        plist_name = None
        app_dir = None
        for name in zf.namelist():
            m = re.match(r"(Payload/[^/]+)/Info\.plist$", name)
            if m:
                plist_name = name
                app_dir = m.group(1)
                break
        if not plist_name:
            return ""
        info = plistlib.load(zf.open(plist_name))

        icons = info.get("CFBundleIcons", {}) or {}
        primary = icons.get("CFBundlePrimaryIcon", {}) or {}
        icon_files = primary.get("CFBundleIconFiles", []) or []
        if not icon_files:
            icon_files = info.get("CFBundleIconFiles", []) or []

        candidates = []
        for name in zf.namelist():
            if not name.startswith(app_dir + "/"):
                continue
            base = os.path.basename(name)
            for pref in icon_files:
                if base.startswith(pref) and base.lower().endswith((".png", "@2x.png", "@3x.png")):
                    candidates.append(name)
        candidates.sort(key=lambda n: ("@3x" not in n, "@2x" not in n, n))
        if not candidates:
            return ""

        icon_name = os.path.splitext(os.path.basename(ipa_path))[0] + ".png"
        dst = os.path.join(out_dir, icon_name)
        with zf.open(candidates[0]) as fsrc, open(dst, "wb") as fdst:
            shutil.copyfileobj(fsrc, fdst)
        return icon_name


def build_app_entry(ipa_path):
    name = os.path.basename(ipa_path)
    info = read_info_plist(ipa_path)

    bundle_id = info.get("CFBundleIdentifier", "")
    version = info.get("CFBundleShortVersionString", info.get("CFBundleVersion", "1.0"))
    app_name = info.get("CFBundleDisplayName") or info.get("CFBundleName") or os.path.splitext(name)[0]
    size = os.path.getsize(ipa_path)

    # 下载地址：优先蓝奏云映射，否则用 GitHub Pages 相对路径
    if name in LANZOU_MAP:
        download_url = LANZOU_MAP[name]
    else:
        download_url = SOURCE_URL.rsplit("/", 1)[0] + "/ipas/" + name

    # 图标
    icon_file = extract_icon(ipa_path, resolve(ICON_DIR))
    icon_url = ""
    if icon_file:
        icon_url = SOURCE_URL.rsplit("/", 1)[0] + "/icons/" + icon_file

    return {
        "name": app_name,
        "bundleID": bundle_id,
        "version": version,
        "versionDate": datetime.date.today().isoformat(),
        "size": size,
        "iconURL": icon_url,
        "downloadURL": download_url,
        "description": app_name,
        "developerName": DEVELOPER_NAME,
        "category": "Utilities",
        "screenshots": [],
        "permissions": []
    }


def main():
    os.makedirs(resolve(IPA_DIR), exist_ok=True)
    os.makedirs(resolve(ICON_DIR), exist_ok=True)

    ipa_dir = resolve(IPA_DIR)
    ipa_files = sorted(f for f in os.listdir(ipa_dir) if f.lower().endswith(".ipa"))

    apps = []
    for f in ipa_files:
        print("处理:", f)
        try:
            apps.append(build_app_entry(os.path.join(ipa_dir, f)))
        except Exception as e:
            print("  跳过（解析失败）:", f, "->", e)

    source = {
        "name": SOURCE_NAME,
        "identifier": SOURCE_IDENTIFIER,
        "subtitle": SUBTITLE,
        "description": DESCRIPTION,
        "iconURL": "",
        "sourceURL": SOURCE_URL,
        "website": WEBSITE,
        "apps": apps
    }

    out_path = resolve(OUTPUT_FILE)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(source, f, ensure_ascii=False, indent=2)

    print(f"\n完成！共 {len(apps)} 个应用，已生成: {out_path}")
    print("源地址:", SOURCE_URL)


if __name__ == "__main__":
    main()
