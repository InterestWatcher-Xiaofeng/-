#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评论智能回复工作流
功能：
1. 采集视频评论
2. 筛选有价值的评论
3. 自动定位并回复指定评论
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from playwright.async_api import async_playwright
from config import base_config
from media_platform.douyin import DouYinCrawler
from tools.comment_filter import CommentFilter
from tools.comment_replier import CommentReplier
import json
from datetime import datetime


class CommentReplyWorkflow:
    """评论智能回复工作流"""

    def __init__(self):
        self.comments_data = []  # 采集的评论数据
        self.filtered_comments = []  # 筛选后的评论
        self.reply_results = []  # 回复结果

    async def run(self):
        """运行完整工作流"""
        print("\n" + "="*60)
        print("🤖 评论智能回复工作流启动")
        print("="*60 + "\n")

        # 步骤1：采集评论
        print("📥 步骤1：采集视频评论")
        await self._step1_collect_comments()

        if not self.comments_data:
            print("❌ 没有采集到评论，工作流结束")
            return

        # 步骤2：筛选评论
        print("\n📋 步骤2：筛选有价值的评论")
        self._step2_filter_comments()

        if not self.filtered_comments:
            print("ℹ️  没有需要回复的评论")
            return

        # 步骤3：人工确认
        print("\n👀 步骤3：人工确认")
        if not self._step3_confirm():
            print("❌ 用户取消操作")
            return

        # 步骤4：自动回复
        print("\n💬 步骤4：自动回复评论")
        await self._step4_auto_reply()

        # 步骤5：生成报告
        print("\n📊 步骤5：生成报告")
        self._step5_generate_report()

        print("\n✅ 工作流完成!")

    async def _step1_collect_comments(self):
        """步骤1：采集评论"""
        # 方式1：从已有文件读取
        data_file = self._find_latest_comment_file()
        if data_file:
            print(f"  📂 从文件读取: {data_file.name}")
            self.comments_data = self._load_comments_from_file(data_file)
            print(f"  ✅ 读取到 {len(self.comments_data)} 条评论")
            return

        # 方式2：实时采集
        print("  🔄 未找到现成文件，开始实时采集...")
        await self._collect_comments_realtime()

    def _find_latest_comment_file(self):
        """查找最新的评论文件"""
        data_dir = Path("data/douyin")
        if not data_dir.exists():
            return None

        # 查找JSON文件
        json_files = list(data_dir.glob("**/*评论*.json"))
        csv_files = list(data_dir.glob("**/*评论*.csv"))

        all_files = json_files + csv_files
        if not all_files:
            return None

        # 返回最新的文件
        return max(all_files, key=lambda f: f.stat().st_mtime)

    def _load_comments_from_file(self, file_path: Path) -> List[Dict]:
        """从文件加载评论"""
        if file_path.suffix == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]

        elif file_path.suffix == ".csv":
            import pandas as pd
            df = pd.read_csv(file_path)
            return df.to_dict('records')

        return []

    async def _collect_comments_realtime(self):
        """实时采集评论"""
        # 这里可以调用现有的爬虫采集评论
        # 为了演示，这里使用模拟数据
        print("  ⚠️  请先使用GUI或命令行采集评论")
        print("  💡 提示：采集完成后，评论会保存在 data/douyin/ 目录")

    def _step2_filter_comments(self):
        """步骤2：筛选评论"""
        filter = CommentFilter()

        # 添加自定义关键词（根据你的业务）
        custom_keywords = [
            "怎么联系", "加微信", "价格", "购买",
            "多少钱", "哪里买", "怎么样", "推荐吗"
        ]
        for kw in custom_keywords:
            filter.add_keyword(kw)

        # 筛选评论
        self.filtered_comments = filter.filter_comments(
            self.comments_data,
            mode="custom"  # 使用自定义模式
        )

        print(f"  原始评论: {len(self.comments_data)} 条")
        print(f"  筛选后: {len(self.filtered_comments)} 条")
        print(f"  筛选率: {len(self.filtered_comments)/len(self.comments_data)*100:.1f}%")

        # 显示筛选结果
        print("\n  需要回复的评论：")
        for i, comment in enumerate(self.filtered_comments[:10], 1):
            content = comment.get("content", "")
            like_count = comment.get("like_count", 0)
            print(f"    {i}. {content[:50]}... (赞:{like_count})")

        if len(self.filtered_comments) > 10:
            print(f"    ... 还有 {len(self.filtered_comments) - 10} 条")

    def _step3_confirm(self) -> bool:
        """步骤3：人工确认"""
        print(f"\n  即将回复 {len(self.filtered_comments)} 条评论")
        print("  回复策略：")
        print("    - 询问价格 → '私信我获取详细价格~'")
        print("    - 询问购买 → '商品链接已私信您~'")
        print("    - 询问效果 → '使用体验很不错，推荐试试~'")
        print("    - 其他问题 → '感谢关注，已私信回复您~'")

        confirm = input("\n  ❓ 确认开始回复吗？(y/n): ")
        return confirm.lower() in ['y', 'yes', '是']

    async def _step4_auto_reply(self):
        """步骤4：自动回复"""
        async with async_playwright() as playwright:
            # 启动浏览器
            print("  🌐 正在启动浏览器...")
            browser = await playwright.chromium.launch(
                headless=False,  # 显示浏览器窗口
                channel="chrome"
            )

            # 加载登录状态
            user_data_dir = Path(f"{base_config.PLATFORM}_user_data_dir")
            if user_data_dir.exists():
                print("  🔑 加载登录状态...")
                context = await browser.new_context(
                    storage_state=str(user_data_dir / "state.json")
                )
            else:
                print("  ⚠️  未找到登录状态，请先登录")
                context = await browser.new_context()

            page = await context.new_page()

            # 创建回复器
            replier = CommentReplier(page)

            # 定义回复策略
            reply_mapping = {
                "多少钱": "私信我获取详细价格~",
                "价格": "私信我获取详细价格~",
                "哪里买": "商品链接已私信您~",
                "购买": "商品链接已私信您~",
                "怎么样": "使用体验很不错，推荐试试~",
                "推荐吗": "使用体验很不错，推荐试试~",
                "微信": "已添加您的微信~",
                "联系": "已私信联系方式~",
                "default": "感谢您的关注，已私信回复您~"
            }

            # 批量回复
            self.reply_results = await replier.batch_reply(
                self.filtered_comments,
                reply_mapping
            )

            print(f"\n  ✅ 回复完成: {len(self.reply_results)} 条")

            await browser.close()

    def _step5_generate_report(self):
        """步骤5：生成报告"""
        # 统计结果
        success_count = sum(1 for r in self.reply_results if r.get("success"))
        fail_count = len(self.reply_results) - success_count

        # 生成报告
        report = {
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "总评论数": len(self.comments_data),
            "筛选后评论数": len(self.filtered_comments),
            "回复成功": success_count,
            "回复失败": fail_count,
            "成功率": f"{success_count/len(self.reply_results)*100:.1f}%" if self.reply_results else "0%",
            "详细结果": self.reply_results
        }

        # 保存报告
        report_file = Path("data/douyin/reply_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"  📄 报告已保存: {report_file}")
        print(f"\n  📊 统计:")
        print(f"    - 总评论: {report['总评论数']}")
        print(f"    - 需回复: {report['筛选后评论数']}")
        print(f"    - 成功: {report['回复成功']}")
        print(f"    - 失败: {report['回复失败']}")
        print(f"    - 成功率: {report['成功率']}")


async def main():
    """主函数"""
    workflow = CommentReplyWorkflow()
    await workflow.run()


if __name__ == "__main__":
    # 运行工作流
    asyncio.run(main())
