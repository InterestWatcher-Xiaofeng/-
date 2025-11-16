#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速回复评论脚本
使用方法：
1. 先采集评论（使用GUI或命令行）
2. 运行此脚本
3. 脚本会自动筛选并回复需要回复的评论
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from playwright.async_api import async_playwright
from tools.comment_replier import CommentReplier
import json


async def quick_reply():
    """快速回复评论"""
    print("\n" + "="*60)
    print("🚀 快速回复评论工具")
    print("="*60 + "\n")

    # === 配置区域 - 根据你的需求修改 ===

    # 1. 视频链接
    video_url = "https://www.douyin.com/video/7525538910311632128"

    # 2. 需要回复的评论（手动指定）
    comments_to_reply = [
        {
            "content": "这个多少钱？",
            "reply": "私信我获取价格哦~",
            "video_url": video_url,
        },
        {
            "content": "哪里可以买？",
            "reply": "商品链接已私信您~",
            "video_url": video_url,
        },
        # 添加更多评论...
    ]

    # === 执行回复 ===

    async with async_playwright() as p:
        # 启动浏览器
        print("🌐 正在启动浏览器...")
        browser = await p.chromium.launch(
            headless=False,  # 显示浏览器
            channel="chrome"
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        # 创建回复器
        replier = CommentReplier(page)

        print(f"\n准备回复 {len(comments_to_reply)} 条评论\n")

        # 逐条回复
        for i, comment in enumerate(comments_to_reply, 1):
            print(f"{'='*60}")
            print(f"📝 [{i}/{len(comments_to_reply)}]")

            result = await replier.reply_to_comment(
                video_url=comment["video_url"],
                comment_content=comment["content"],
                reply_text=comment["reply"]
            )

            if result["success"]:
                print(f"✅ 成功: {comment['content'][:30]}")
            else:
                print(f"❌ 失败: {comment['content'][:30]} - {result['message']}")

            # 延迟，避免频繁操作
            if i < len(comments_to_reply):
                print("\n⏱️  等待5秒...")
                await asyncio.sleep(5)

        print(f"\n{'='*60}")
        print("✅ 所有评论回复完成!")

        await browser.close()


async def auto_reply_from_file():
    """从文件自动加载评论并回复"""
    print("\n" + "="*60)
    print("📁 从文件加载评论并自动回复")
    print("="*60 + "\n")

    # 查找最新的评论文件
    data_dir = Path("data/douyin")
    if not data_dir.exists():
        print("❌ 未找到评论数据目录: data/douyin")
        return

    json_files = list(data_dir.glob("**/*评论*.json"))
    if not json_files:
        print("❌ 未找到评论JSON文件")
        print("💡 请先使用GUI或命令行采集评论")
        return

    # 选择最新的文件
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    print(f"📂 读取文件: {latest_file.name}")

    # 加载评论
    with open(latest_file, 'r', encoding='utf-8') as f:
        comments = json.load(f)
        if not isinstance(comments, list):
            comments = [comments]

    print(f"✅ 加载到 {len(comments)} 条评论")

    # 筛选需要回复的评论（简单示例）
    keywords = ["多少钱", "哪里买", "怎么联系", "价格", "购买", "？"]
    filtered = []

    for comment in comments:
        content = comment.get("content", "")
        # 检查是否包含关键词
        if any(kw in content for kw in keywords):
            filtered.append(comment)

    print(f"🔍 筛选后需回复: {len(filtered)} 条")

    if not filtered:
        print("ℹ️  没有需要回复的评论")
        return

    # 显示前5条
    print("\n预览（前5条）：")
    for i, c in enumerate(filtered[:5], 1):
        print(f"  {i}. {c.get('content', '')[:50]}...")

    # 确认
    confirm = input("\n❓ 确认开始回复吗？(y/n): ")
    if confirm.lower() not in ['y', 'yes', '是']:
        print("❌ 已取消")
        return

    # 定义回复策略
    def get_reply_text(content):
        if "多少钱" in content or "价格" in content:
            return "私信我获取详细价格~"
        elif "哪里买" in content or "购买" in content:
            return "商品链接已私信您~"
        elif "怎么联系" in content or "微信" in content:
            return "已私信联系方式~"
        else:
            return "感谢关注，已私信回复您~"

    # 启动浏览器并回复
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")
        context = await browser.new_context()
        page = await context.new_page()

        replier = CommentReplier(page)

        success = 0
        for i, comment in enumerate(filtered, 1):
            video_url = comment.get("video_url", "")
            if not video_url:
                # 如果评论中没有video_url，尝试从aweme_id构建
                aweme_id = comment.get("aweme_id")
                if aweme_id:
                    video_url = f"https://www.douyin.com/video/{aweme_id}"
                else:
                    print(f"⚠️  跳过: 缺少视频链接")
                    continue

            content = comment.get("content", "")
            reply_text = get_reply_text(content)

            print(f"\n[{i}/{len(filtered)}] 回复: {content[:30]}...")

            result = await replier.reply_to_comment(
                video_url=video_url,
                comment_content=content,
                reply_text=reply_text,
                comment_id=comment.get("comment_id")
            )

            if result["success"]:
                success += 1
                print(f"✅ 成功")
            else:
                print(f"❌ 失败: {result['message']}")

            await asyncio.sleep(5)

        print(f"\n{'='*60}")
        print(f"✅ 完成! 成功: {success}/{len(filtered)}")

        await browser.close()


def show_menu():
    """显示菜单"""
    print("\n" + "="*60)
    print("🤖 评论智能回复工具")
    print("="*60)
    print("\n请选择模式：")
    print("  1. 快速回复（手动指定评论）")
    print("  2. 自动回复（从文件加载）")
    print("  3. 退出")
    print()

    choice = input("请输入选项 (1-3): ")
    return choice


async def main():
    while True:
        choice = show_menu()

        if choice == "1":
            await quick_reply()
        elif choice == "2":
            await auto_reply_from_file()
        elif choice == "3":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选项")

        input("\n按Enter继续...")


if __name__ == "__main__":
    asyncio.run(main())
