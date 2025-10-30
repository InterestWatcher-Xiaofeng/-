#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 统一浏览器采集器
解决GUI登录和爬虫采集使用不同浏览器实例的问题
使用同一个浏览器窗口进行登录和后续数据采集
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

import config
from media_platform.douyin.core import DouYinCrawler
from tools.utils import utils

class UnifiedBrowserCrawler:
    """统一浏览器采集器"""
    
    def __init__(self, shared_context=None, shared_page=None, progress_callback=None):
        """
        初始化统一浏览器采集器

        Args:
            shared_context: GUI提供的共享浏览器上下文
            shared_page: GUI提供的共享页面
            progress_callback: 进度回调函数 callback(current, total, message)
        """
        self.shared_context = shared_context
        self.shared_page = shared_page
        self.crawler = None
        self.progress_callback = progress_callback
        
    async def setup_crawler(self, platform: str = "dy"):
        """设置爬虫实例"""
        if platform == "dy":
            self.crawler = DouYinCrawler()
            # 🔥 关键：将共享浏览器上下文注入到爬虫中
            if hasattr(self.crawler, 'browser_context'):
                self.crawler.browser_context = self.shared_context
            if hasattr(self.crawler, 'context'):
                self.crawler.context = self.shared_context
        else:
            raise ValueError(f"暂不支持平台: {platform}")
    
    async def start_search_crawling(self, keywords: str, max_count: int = 20,
                                    max_comments_per_video: int = 50,
                                    enable_comments: bool = True,
                                    enable_sub_comments: bool = True,
                                    save_format: str = "csv",
                                    output_dir: str = None):
        """
        开始搜索采集

        Args:
            keywords: 搜索关键词
            max_count: 最大采集数量（视频数量）
            max_comments_per_video: 每个视频最大评论数量
            enable_comments: 是否采集一级评论
            enable_sub_comments: 是否采集二级评论
            save_format: 保存格式 (csv/json/sqlite/db)
            output_dir: 输出目录（如果为None则使用默认目录）
        """
        try:
            # 🔥 设置完整配置
            config.KEYWORDS = keywords
            config.CRAWLER_MAX_NOTES_COUNT = max_count
            config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = max_comments_per_video
            config.CRAWLER_TYPE = "search"
            config.PLATFORM = "dy"
            config.ENABLE_GET_COMMENTS = enable_comments
            config.ENABLE_GET_SUB_COMMENTS = enable_sub_comments
            config.SAVE_DATA_OPTION = save_format

            # 🔥 每次采集前重置store实例和视频信息缓存
            # 这样可以确保每次采集都创建新的文件（带新的时间戳）
            from store.douyin import DouyinStoreFactory
            import store.douyin as douyin_store

            DouyinStoreFactory.reset_store()  # 重置store实例
            douyin_store._video_info_cache.clear()  # 清空视频信息缓存

            # 🔥 设置输出目录
            if output_dir:
                DouyinStoreFactory.set_output_dir(output_dir)
                print(f"📁 设置输出目录: {output_dir}")

            print(f"🚀 开始统一浏览器采集")
            print(f"🔍 关键词: {keywords}")
            print(f"📊 视频数量: {max_count} 个")
            print(f"💬 每个视频评论数: {max_comments_per_video} 条")
            print(f"✅ 一级评论: {enable_comments}")
            print(f"✅ 二级评论: {enable_sub_comments}")
            print(f"💾 保存格式: {save_format}")
            print(f"🔥 使用共享浏览器上下文")

            # 设置爬虫
            await self.setup_crawler("dy")

            # 🔥 关键：使用统一浏览器进行采集
            if self.crawler:
                await self.start_unified_douyin_crawling()

            print(f"✅ 采集完成！")

            # 🔥 返回生成的文件路径（传递关键词用于文件命名）
            return self._get_generated_files(save_format, output_dir, keywords)

        except Exception as e:
            print(f"❌ 采集失败: {str(e)}")
            raise

    def _get_generated_files(self, save_format: str, output_dir: str = None, keywords: str = "") -> dict:
        """
        获取生成的文件路径

        🔥 新命名规则：平台_关键词.格式
        示例：抖音_美食探店.csv
        """
        import os
        import re
        from tools.utils import utils

        if output_dir:
            base_path = output_dir
        else:
            base_path = f"data/douyin/{save_format}"

        # 🔥 清理关键词，移除特殊字符
        clean_keywords = re.sub(r'[\\/:*?"<>|\s]+', '_', keywords.strip())
        if not clean_keywords:
            clean_keywords = "未命名"

        # 🔥 新命名格式：平台_关键词
        platform_name = "抖音"
        files = {
            "contents": f"{base_path}/{platform_name}_{clean_keywords}_内容.{save_format}",
            "comments": f"{base_path}/{platform_name}_{clean_keywords}_评论.{save_format}"
        }

        # 只返回存在的文件
        existing_files = {}
        for key, path in files.items():
            if os.path.exists(path):
                existing_files[key] = path
                print(f"📄 {key}文件: {path}")

        return existing_files

    async def start_unified_douyin_crawling(self):
        """🔥 使用统一浏览器进行抖音采集"""
        try:
            # 🔥 关键修复：标记这是统一浏览器模式，不要关闭浏览器上下文
            self.crawler._is_unified_browser = True

            # 直接设置浏览器上下文，跳过浏览器启动
            self.crawler.browser_context = self.shared_context
            self.crawler.context_page = self.shared_page

            # 🔥 传递进度回调给爬虫
            if self.progress_callback:
                self.crawler.progress_callback = self.progress_callback

            # 🔥 每次采集都重新创建抖音客户端，确保使用最新的cookies
            from media_platform.douyin.client import DouYinClient
            print("🔄 创建新的抖音客户端...")
            self.crawler.dy_client = await self.crawler.create_douyin_client(None)

            # 检查登录状态
            print("🔍 检查登录状态...")
            if not await self.crawler.dy_client.pong(browser_context=self.shared_context):
                print("⚠️ 登录状态检查失败，但继续尝试采集...")

            # 更新客户端cookies
            print("🍪 更新客户端cookies...")
            await self.crawler.dy_client.update_cookies(browser_context=self.shared_context)

            # 开始搜索
            from var import crawler_type_var
            crawler_type_var.set(config.CRAWLER_TYPE)

            print("🔍 开始搜索采集...")
            await self.crawler.search()

            print("✅ 搜索采集完成")

        except Exception as e:
            print(f"❌ 统一浏览器抖音采集失败: {e}")
            import traceback
            traceback.print_exc()
            raise

async def run_unified_crawler(keywords: str, shared_context=None, shared_page=None,
                             max_count: int = 20, max_comments_per_video: int = 50,
                             enable_comments: bool = True, enable_sub_comments: bool = True,
                             save_format: str = "csv", output_dir: str = None,
                             progress_callback=None):
    """
    运行统一浏览器采集器

    Args:
        keywords: 搜索关键词
        shared_context: 共享浏览器上下文
        shared_page: 共享页面
        max_count: 最大采集数量（视频数量）
        max_comments_per_video: 每个视频最大评论数量
        enable_comments: 是否采集一级评论
        enable_sub_comments: 是否采集二级评论
        save_format: 保存格式 (csv/json/sqlite/db)
        output_dir: 输出目录
        progress_callback: 进度回调函数 callback(current, total, message)

    Returns:
        dict: 生成的文件路径字典 {"contents": "path/to/contents.csv", "comments": "path/to/comments.csv"}
    """
    crawler = UnifiedBrowserCrawler(shared_context, shared_page, progress_callback)
    return await crawler.start_search_crawling(
        keywords=keywords,
        max_count=max_count,
        max_comments_per_video=max_comments_per_video,
        enable_comments=enable_comments,
        enable_sub_comments=enable_sub_comments,
        save_format=save_format,
        output_dir=output_dir
    )

def main():
    """主函数 - 用于测试"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🔥 统一浏览器采集器")
    parser.add_argument("--keywords", "-k", required=True, help="搜索关键词")
    parser.add_argument("--max-count", "-c", type=int, default=20, help="最大采集数量")
    
    args = parser.parse_args()
    
    print("⚠️ 注意：此脚本需要与GUI应用配合使用")
    print("请通过GUI应用启动统一浏览器采集")

if __name__ == "__main__":
    main()
