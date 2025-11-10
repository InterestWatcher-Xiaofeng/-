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

    def __init__(self, shared_context=None, shared_page=None, progress_callback=None, stop_flag_callback=None, gui_app=None):
        """
        初始化统一浏览器采集器

        Args:
            shared_context: GUI提供的共享浏览器上下文
            shared_page: GUI提供的共享页面
            progress_callback: 进度回调函数 callback(current, total, message)
            stop_flag_callback: 停止标志检查函数 callback() -> bool
            gui_app: GUI应用实例，用于设置验证状态
        """
        self.shared_context = shared_context
        self.shared_page = shared_page
        self.crawler = None
        self.progress_callback = progress_callback
        self.stop_flag_callback = stop_flag_callback
        self.gui_app = gui_app  # 🔥 新增：GUI应用实例

    def should_stop(self):
        """检查是否应该停止采集"""
        if self.stop_flag_callback:
            return self.stop_flag_callback()
        return False
        
    async def setup_crawler(self, platform: str = "dy"):
        """设置爬虫实例"""
        if platform == "dy":
            self.crawler = DouYinCrawler()
            # 🔥 关键：将共享浏览器上下文注入到爬虫中
            if hasattr(self.crawler, 'browser_context'):
                self.crawler.browser_context = self.shared_context
            if hasattr(self.crawler, 'context'):
                self.crawler.context = self.shared_context
        elif platform == "xhs":
            from media_platform.xhs import XiaoHongShuCrawler
            self.crawler = XiaoHongShuCrawler()
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
                                    output_dir: str = None,
                                    platform: str = "dy"):
        """
        开始搜索采集

        Args:
            keywords: 搜索关键词
            max_count: 最大采集数量（视频/笔记数量）
            max_comments_per_video: 每个视频/笔记最大评论数量
            enable_comments: 是否采集一级评论
            enable_sub_comments: 是否采集二级评论
            save_format: 保存格式 (csv/json/sqlite/db)
            output_dir: 输出目录（如果为None则使用默认目录）
            platform: 平台 (dy/xhs)
        """
        try:
            # 🔥 设置完整配置
            config.KEYWORDS = keywords
            config.CRAWLER_MAX_NOTES_COUNT = max_count
            config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = max_comments_per_video
            config.CRAWLER_TYPE = "search"
            config.PLATFORM = platform  # 🔥 使用传入的平台参数
            config.ENABLE_GET_COMMENTS = enable_comments
            config.ENABLE_GET_SUB_COMMENTS = enable_sub_comments
            config.SAVE_DATA_OPTION = save_format
            config.ENABLE_RPA_SEARCH = True  # 🔥 启用RPA搜索模式

            # 🔥 每次采集前重置store实例和缓存
            if platform == "dy":
                from store.douyin import DouyinStoreFactory
                import store.douyin as douyin_store
                DouyinStoreFactory.reset_store()
                douyin_store._video_info_cache.clear()
                if output_dir:
                    DouyinStoreFactory.set_output_dir(output_dir)
                content_type = "视频"
            elif platform == "xhs":
                from store.xhs import XhsStoreFactory
                import store.xhs as xhs_store
                XhsStoreFactory.reset_store()
                if hasattr(xhs_store, '_note_info_cache'):
                    xhs_store._note_info_cache.clear()
                if output_dir:
                    XhsStoreFactory.set_output_dir(output_dir)
                content_type = "笔记"
            else:
                content_type = "内容"

            print(f"🚀 开始统一浏览器采集 - {platform.upper()}")
            print(f"🔍 关键词: {keywords}")
            print(f"📊 {content_type}数量: {max_count} 个")
            print(f"💬 每个{content_type}评论数: {max_comments_per_video} 条")
            print(f"✅ 一级评论: {enable_comments}")
            print(f"✅ 二级评论: {enable_sub_comments}")
            print(f"💾 保存格式: {save_format}")
            print(f"🔥 使用共享浏览器上下文")

            # 设置爬虫
            await self.setup_crawler(platform)

            # 🔥 关键：使用统一浏览器进行采集
            if self.crawler:
                if platform == "dy":
                    await self.start_unified_douyin_crawling()
                elif platform == "xhs":
                    await self.start_unified_xiaohongshu_crawling()

            print(f"✅ 采集完成！")

            # 🔥 返回生成的文件路径（传递关键词用于文件命名）
            return self._get_generated_files(save_format, output_dir, keywords, platform)

        except Exception as e:
            print(f"❌ 采集失败: {str(e)}")
            raise

    def _get_generated_files(self, save_format: str, output_dir: str = None, keywords: str = "", platform: str = "dy") -> dict:
        """
        获取生成的文件路径

        🔥 新命名规则：平台_关键词.格式
        示例：抖音_美食探店.csv, 小红书_美食探店.csv
        """
        import os
        import re

        # 🔥 根据平台设置默认路径和平台名称
        platform_names = {
            "dy": "抖音",
            "xhs": "小红书",
            "bili": "B站",
            "ks": "快手",
            "wb": "微博",
            "tieba": "贴吧",
            "zhihu": "知乎"
        }
        platform_name = platform_names.get(platform, platform.upper())

        if output_dir:
            base_path = output_dir
        else:
            platform_dirs = {
                "dy": "douyin",
                "xhs": "xhs",
                "bili": "bilibili",
                "ks": "kuaishou",
                "wb": "weibo",
                "tieba": "tieba",
                "zhihu": "zhihu"
            }
            platform_dir = platform_dirs.get(platform, platform)
            base_path = f"data/{platform_dir}/{save_format}"

        # 🔥 清理关键词，移除特殊字符
        clean_keywords = re.sub(r'[\\/:*?"<>|\s]+', '_', keywords.strip())
        if not clean_keywords:
            clean_keywords = "未命名"

        # 🔥 新命名格式：平台_关键词
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

    async def start_detail_crawling(self, video_url: str,
                                    max_comments_per_video: int = 50,
                                    enable_comments: bool = True,
                                    enable_sub_comments: bool = True,
                                    save_format: str = "csv",
                                    output_dir: str = None):
        """
        开始链接采集 (Detail模式)

        Args:
            video_url: 视频链接或ID
            max_comments_per_video: 每个视频最大评论数量
            enable_comments: 是否采集一级评论
            enable_sub_comments: 是否采集二级评论
            save_format: 保存格式 (csv/json/sqlite/db)
            output_dir: 输出目录
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 开始链接采集")
            print(f"{'='*60}")
            print(f"🔗 视频链接: {video_url}")
            print(f"💬 评论数: {max_comments_per_video} 条")
            print(f"💾 保存格式: {save_format}")
            print(f"{'='*60}\n")

            # 🔥 验证链接格式
            from media_platform.douyin.help import parse_video_info_from_url
            try:
                video_info = parse_video_info_from_url(video_url)
                print(f"✅ 链接解析成功:")
                print(f"   视频ID: {video_info.aweme_id}")
                print(f"   链接类型: {video_info.url_type}")
            except Exception as parse_error:
                print(f"❌ 链接解析失败: {parse_error}")
                print(f"   请检查链接格式是否正确")
                print(f"   支持的格式:")
                print(f"   1. 完整链接: https://www.douyin.com/video/7525538910311632128")
                print(f"   2. 短链接: https://v.douyin.com/drIPtQ_WPWY/")
                print(f"   3. 纯ID: 7525538910311632128")
                raise

            # 🔥 设置配置
            config.DY_SPECIFIED_ID_LIST = [video_url]  # 单个链接
            config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = max_comments_per_video
            config.CRAWLER_TYPE = "detail"
            config.PLATFORM = "dy"
            config.ENABLE_GET_COMMENTS = enable_comments
            config.ENABLE_GET_SUB_COMMENTS = enable_sub_comments
            config.SAVE_DATA_OPTION = save_format

            # 🔥 重置store
            from store.douyin import DouyinStoreFactory
            import store.douyin as douyin_store
            DouyinStoreFactory.reset_store()
            douyin_store._video_info_cache.clear()

            if output_dir:
                DouyinStoreFactory.set_output_dir(output_dir)

            # 设置爬虫
            await self.setup_crawler("dy")

            # 开始采集
            if self.crawler:
                await self.start_unified_douyin_crawling()

            print(f"\n✅ 链接采集完成！\n")

            # 返回生成的文件
            return self._get_generated_files(save_format, output_dir, video_url)

        except Exception as e:
            print(f"\n❌ 链接采集失败: {str(e)}\n")
            import traceback
            traceback.print_exc()
            raise

    async def start_creator_crawling(self, creator_url: str, max_count: int = 20,
                                     max_comments_per_video: int = 50,
                                     enable_comments: bool = True,
                                     enable_sub_comments: bool = True,
                                     save_format: str = "csv",
                                     output_dir: str = None):
        """
        开始创作者采集 (Creator模式)

        Args:
            creator_url: 创作者链接或ID
            max_count: 最大采集视频数量
            max_comments_per_video: 每个视频最大评论数量
            enable_comments: 是否采集一级评论
            enable_sub_comments: 是否采集二级评论
            save_format: 保存格式 (csv/json/sqlite/db)
            output_dir: 输出目录
        """
        try:
            # 🔥 设置配置
            config.DY_CREATOR_ID_LIST = [creator_url]  # 单个创作者
            config.CRAWLER_MAX_NOTES_COUNT = max_count
            config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = max_comments_per_video
            config.CRAWLER_TYPE = "creator"
            config.PLATFORM = "dy"
            config.ENABLE_GET_COMMENTS = enable_comments
            config.ENABLE_GET_SUB_COMMENTS = enable_sub_comments
            config.SAVE_DATA_OPTION = save_format

            # 🔥 重置store
            from store.douyin import DouyinStoreFactory
            import store.douyin as douyin_store
            DouyinStoreFactory.reset_store()
            douyin_store._video_info_cache.clear()

            if output_dir:
                DouyinStoreFactory.set_output_dir(output_dir)

            print(f"🚀 开始创作者采集")
            print(f"👤 创作者: {creator_url}")
            print(f"📊 视频数量: {max_count} 个")
            print(f"💬 每个视频评论数: {max_comments_per_video} 条")
            print(f"💾 保存格式: {save_format}")

            # 设置爬虫
            await self.setup_crawler("dy")

            # 开始采集
            if self.crawler:
                await self.start_unified_douyin_crawling()

            print(f"✅ 创作者采集完成！")

            # 返回生成的文件
            return self._get_generated_files(save_format, output_dir, creator_url)

        except Exception as e:
            print(f"❌ 创作者采集失败: {str(e)}")
            raise

    async def start_unified_douyin_crawling(self):
        """🔥 使用统一浏览器进行抖音采集 - 支持三种模式"""
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

                # 🔥 设置验证状态标志
                if self.gui_app:
                    self.gui_app.is_verifying = True

                # 🔥 弹窗提示用户可能需要验证
                import tkinter.messagebox as messagebox
                import threading
                def show_warning():
                    messagebox.showwarning(
                        "登录验证提示",
                        "检测到可能需要登录验证！\n\n"
                        "请在浏览器中完成以下操作：\n"
                        "1. 扫码登录（如果需要）\n"
                        "2. 完成手机号验证（如果需要）\n"
                        "3. 完成滑动验证码（如果需要）\n\n"
                        "验证完成后，采集将自动继续。\n"
                        "此过程中点击【停止采集】按钮无效。"
                    )
                # 在新线程中显示弹窗，避免阻塞
                threading.Thread(target=show_warning, daemon=True).start()
                # 等待60秒，给用户时间验证
                print("⏳ 等待60秒，给用户时间完成验证...")
                await asyncio.sleep(60)

                # 🔥 验证完成，清除验证状态标志
                if self.gui_app:
                    self.gui_app.is_verifying = False

            # 更新客户端cookies
            print("🍪 更新客户端cookies...")
            await self.crawler.dy_client.update_cookies(browser_context=self.shared_context)

            # 🔥 根据模式执行不同的采集
            from var import crawler_type_var
            crawler_type_var.set(config.CRAWLER_TYPE)

            if config.CRAWLER_TYPE == "search":
                # 🔥 使用RPA搜索模式
                if config.ENABLE_RPA_SEARCH:
                    print("🔍 开始RPA搜索采集...")
                    await self._rpa_search_and_collect()
                else:
                    print("🔍 开始API搜索采集...")
                    await self.crawler.search()
            elif config.CRAWLER_TYPE == "detail":
                print("🔗 开始链接采集...")
                await self.crawler.get_specified_awemes()
            elif config.CRAWLER_TYPE == "creator":
                print("👤 开始创作者采集...")
                await self.crawler.get_creators_and_videos()
            else:
                raise ValueError(f"未知的采集模式: {config.CRAWLER_TYPE}")

            print(f"✅ {config.CRAWLER_TYPE}采集完成")

        except Exception as e:
            print(f"❌ 统一浏览器抖音采集失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
            print(f"   错误详情: {repr(e)}")
            import traceback
            print(f"   完整堆栈:")
            traceback.print_exc()
            raise Exception(f"统一浏览器采集失败: {type(e).__name__}: {str(e)}") from e

    async def start_unified_xiaohongshu_crawling(self):
        """🔥 使用统一浏览器进行小红书采集 - 支持三种模式"""
        try:
            # 🔥 关键修复：标记这是统一浏览器模式，不要关闭浏览器上下文
            self.crawler._is_unified_browser = True

            # 直接设置浏览器上下文，跳过浏览器启动
            self.crawler.browser_context = self.shared_context
            self.crawler.context_page = self.shared_page

            # 🔥 传递进度回调给爬虫
            if self.progress_callback:
                self.crawler.progress_callback = self.progress_callback

            # 🔥 每次采集都重新创建小红书客户端，确保使用最新的cookies
            from media_platform.xhs.client import XiaoHongShuClient
            print("🔄 创建新的小红书客户端...")
            self.crawler.xhs_client = await self.crawler.create_xhs_client(None)

            # 检查登录状态
            print("🔍 检查登录状态...")
            if not await self.crawler.xhs_client.pong():
                print("⚠️ 登录状态检查失败，但继续尝试采集...")

                # 🔥 设置验证状态标志
                if self.gui_app:
                    self.gui_app.is_verifying = True

                # 🔥 弹窗提示用户可能需要验证
                import tkinter.messagebox as messagebox
                import threading
                def show_warning():
                    messagebox.showwarning(
                        "登录验证提示",
                        "检测到可能需要登录验证！\n\n"
                        "请在浏览器中完成以下操作：\n"
                        "1. 扫码登录（如果需要）\n"
                        "2. 完成滑动验证码（如果需要）\n\n"
                        "验证完成后，采集将自动继续。\n"
                        "此过程中点击【停止采集】按钮无效。"
                    )
                # 在新线程中显示弹窗，避免阻塞
                threading.Thread(target=show_warning, daemon=True).start()
                # 等待60秒，给用户时间验证
                print("⏳ 等待60秒，给用户时间完成验证...")
                await asyncio.sleep(60)

                # 🔥 验证完成，清除验证状态标志
                if self.gui_app:
                    self.gui_app.is_verifying = False

            # 更新客户端cookies
            print("🍪 更新客户端cookies...")
            await self.crawler.xhs_client.update_cookies(browser_context=self.shared_context)

            # 🔥 根据模式执行不同的采集
            from var import crawler_type_var
            crawler_type_var.set(config.CRAWLER_TYPE)

            if config.CRAWLER_TYPE == "search":
                # 🔥 使用RPA搜索模式
                if config.ENABLE_RPA_SEARCH:
                    print("🔍 开始RPA搜索采集...")
                    await self._rpa_search_and_collect()
                else:
                    print("🔍 开始API搜索采集...")
                    await self.crawler.search()
            elif config.CRAWLER_TYPE == "detail":
                print("🔗 开始链接采集...")
                await self.crawler.get_specified_notes()
            elif config.CRAWLER_TYPE == "creator":
                print("👤 开始创作者采集...")
                await self.crawler.get_creators_and_notes()
            else:
                raise ValueError(f"未知的采集模式: {config.CRAWLER_TYPE}")

            print(f"✅ {config.CRAWLER_TYPE}采集完成")

        except Exception as e:
            print(f"❌ 统一浏览器小红书采集失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
            print(f"   错误详情: {repr(e)}")
            import traceback
            print(f"   完整堆栈:")
            traceback.print_exc()
            raise Exception(f"统一浏览器采集失败: {type(e).__name__}: {str(e)}") from e

    async def _rpa_search_and_collect(self):
        """🔥 RPA搜索并收集链接,然后抓取评论 - 支持抖音和小红书"""
        import asyncio

        # 🔥 根据平台选择不同的RPA爬虫
        if config.PLATFORM == "dy":
            from rpa_search_crawler import RPASearchCrawler

            # 获取关键词
            keyword = config.KEYWORDS.split(',')[0].strip()
            max_count = config.CRAWLER_MAX_NOTES_COUNT

            print(f"🎯 抖音RPA搜索参数:")
            print(f"   关键词: {keyword}")
            print(f"   视频数量: {max_count}")

            # 创建RPA搜索爬虫(使用共享浏览器)
            rpa_crawler = RPASearchCrawler(keyword=keyword, max_videos=max_count)

            # 🔥 关键:使用共享浏览器上下文
            rpa_crawler.context = self.shared_context
            rpa_crawler.page = self.shared_page

            # 执行RPA搜索(跳过浏览器启动和登录)
            print("🔍 开始RPA搜索...")
            await rpa_crawler._goto_search_page()
            await rpa_crawler._search_keyword()
            await rpa_crawler._scroll_and_collect_links()

            links = rpa_crawler.video_links
            print(f"✅ RPA搜索完成,收集到 {len(links)} 个视频链接")

            # 🔥 将链接设置到配置,然后调用detail模式抓取
            if links:
                config.DY_SPECIFIED_ID_LIST = links
                config.CRAWLER_TYPE = "detail"  # 切换到detail模式
                # 🔥 注意:CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES已经在start_search_crawling()中设置了

                print("🔗 开始抓取视频评论...")
                print(f"   每个视频评论数: {config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES} 条")
                await self.crawler.get_specified_awemes()
            else:
                print("⚠️ 未收集到视频链接,跳过评论抓取")

        elif config.PLATFORM == "xhs":
            from rpa_xhs_search_crawler import RPAXhsSearchCrawler

            # 获取关键词
            keyword = config.KEYWORDS.split(',')[0].strip()
            max_count = config.CRAWLER_MAX_NOTES_COUNT

            print(f"🎯 小红书RPA搜索参数:")
            print(f"   关键词: {keyword}")
            print(f"   笔记数量: {max_count}")

            # 创建RPA搜索爬虫(使用共享浏览器)
            rpa_crawler = RPAXhsSearchCrawler(keyword=keyword, max_notes=max_count)

            # 🔥 关键:使用共享浏览器上下文
            rpa_crawler.context = self.shared_context
            rpa_crawler.page = self.shared_page

            # 执行RPA搜索(跳过浏览器启动和登录)
            print("🔍 开始RPA搜索...")
            await rpa_crawler._goto_search_page()
            await rpa_crawler._search_keyword()
            await rpa_crawler._scroll_and_collect_links()

            # 🔥 新流程: 直接在RPA中逐个点击笔记并抓取评论
            if hasattr(rpa_crawler, 'ready_to_click') and rpa_crawler.ready_to_click:
                print(f"\n🔥 开始模拟真实用户: 从左到右依次点击笔记并抓取评论")

                # 获取小红书客户端
                xhs_client = self.crawler.xhs_client

                # 🔥 调用新方法: 逐个点击笔记并直接抓取评论
                all_notes_data = await rpa_crawler.click_and_scrape_notes(xhs_client)

                # 🔥 将数据保存到crawler中
                if all_notes_data:
                    print(f"\n✅ 成功抓取 {len(all_notes_data)} 个笔记的数据")

                    # 将数据转换为crawler需要的格式并保存
                    for note_data in all_notes_data:
                        note_detail = note_data.get('note_detail')
                        comments = note_data.get('comments', [])

                        if note_detail:
                            # 保存笔记详情
                            await self.crawler.xhs_store.store_content(note_detail)

                            # 保存评论
                            if comments:
                                await self.crawler.batch_update_note_comments(note_detail['note_id'], comments)

                    print(f"✅ 所有数据已保存")
                else:
                    print("⚠️ 未成功抓取到数据")
            else:
                print("⚠️ 页面未准备好,跳过抓取")
        else:
            print(f"⚠️ 平台 {config.PLATFORM} 暂不支持RPA搜索模式")

async def run_unified_crawler(keywords: str = None, video_url: str = None, note_url: str = None, creator_url: str = None,
                             crawler_mode: str = "search",
                             shared_context=None, shared_page=None,
                             max_count: int = 20, max_comments_per_video: int = 50, max_comments_per_note: int = 50,
                             enable_comments: bool = True, enable_sub_comments: bool = True,
                             save_format: str = "csv", output_dir: str = None,
                             progress_callback=None, stop_flag_callback=None, platform: str = "dy"):
    """
    运行统一浏览器采集器 - 支持三种模式,支持抖音和小红书

    Args:
        keywords: 搜索关键词 (search模式)
        video_url: 视频链接 (detail模式 - 抖音)
        note_url: 笔记链接 (detail模式 - 小红书)
        creator_url: 创作者链接 (creator模式)
        crawler_mode: 采集模式 (search/detail/creator)
        shared_context: 共享浏览器上下文
        shared_page: 共享页面
        max_count: 最大采集数量（视频/笔记数量）
        max_comments_per_video: 每个视频最大评论数量（抖音）
        max_comments_per_note: 每个笔记最大评论数量（小红书）
        enable_comments: 是否采集一级评论
        enable_sub_comments: 是否采集二级评论
        save_format: 保存格式 (csv/json/sqlite/db)
        output_dir: 输出目录
        progress_callback: 进度回调函数 callback(current, total, message)
        stop_flag_callback: 停止标志检查函数 callback() -> bool
        platform: 平台 (dy/xhs)

    Returns:
        dict: 生成的文件路径字典 {"contents": "path/to/contents.csv", "comments": "path/to/comments.csv"}
    """
    crawler = UnifiedBrowserCrawler(shared_context, shared_page, progress_callback, stop_flag_callback)

    # 🔥 根据平台选择评论数量参数
    max_comments = max_comments_per_note if platform == "xhs" else max_comments_per_video
    content_url = note_url if platform == "xhs" else video_url

    if crawler_mode == "search":
        return await crawler.start_search_crawling(
            keywords=keywords,
            max_count=max_count,
            max_comments_per_video=max_comments,
            enable_comments=enable_comments,
            enable_sub_comments=enable_sub_comments,
            save_format=save_format,
            output_dir=output_dir,
            platform=platform  # 🔥 传递平台参数
        )
    elif crawler_mode == "detail":
        return await crawler.start_detail_crawling(
            video_url=content_url,
            max_comments_per_video=max_comments,
            enable_comments=enable_comments,
            enable_sub_comments=enable_sub_comments,
            save_format=save_format,
            output_dir=output_dir
        )
    elif crawler_mode == "creator":
        return await crawler.start_creator_crawling(
            creator_url=creator_url,
            max_count=max_count,
            max_comments_per_video=max_comments,
            enable_comments=enable_comments,
            enable_sub_comments=enable_sub_comments,
            save_format=save_format,
            output_dir=output_dir
        )
    else:
        raise ValueError(f"未知的采集模式: {crawler_mode}")

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
