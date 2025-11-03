"""
RPA模式搜索爬虫 - 混合方案
功能: 使用RPA模式搜索关键词,获取视频链接,然后用Detail模式抓取评论
"""

import asyncio
import re
import json
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright, Page, Browser
from datetime import datetime

from config import base_config


class RPASearchCrawler:
    """RPA模式搜索爬虫"""
    
    def __init__(self, keyword: str, max_videos: int = 20):
        self.keyword = keyword
        self.max_videos = max_videos
        self.video_links = []
        self.browser = None
        self.context = None
        self.page = None
        
    async def start(self):
        """启动爬虫"""
        print("=" * 60)
        print("🚀 RPA模式搜索爬虫启动")
        print("=" * 60)
        print(f"🔍 关键词: {self.keyword}")
        print(f"🎬 目标视频数: {self.max_videos}")
        print("=" * 60)
        
        async with async_playwright() as playwright:
            # 启动浏览器
            await self._launch_browser(playwright)
            
            # 访问抖音搜索页
            await self._goto_search_page()
            
            # 等待用户登录
            await self._wait_for_login()
            
            # 执行搜索
            await self._search_keyword()
            
            # 滚动加载视频
            await self._scroll_and_collect_links()
            
            # 保存链接
            self._save_links()
            
            # 关闭浏览器
            await self._close_browser()
            
        return self.video_links
    
    async def _launch_browser(self, playwright):
        """启动浏览器"""
        print("\n📱 正在启动浏览器...")
        
        self.browser = await playwright.chromium.launch(
            headless=False,  # 显示浏览器
            channel="chrome"  # 使用Chrome
        )
        
        # 创建浏览器上下文
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        # 创建页面
        self.page = await self.context.new_page()
        
        print("✅ 浏览器启动成功")
    
    async def _goto_search_page(self):
        """访问抖音搜索页"""
        print("\n🌐 正在访问抖音搜索页...")

        url = "https://www.douyin.com/"
        try:
            await self.page.goto(url, timeout=60000)  # 增加超时时间到60秒
            await asyncio.sleep(3)  # 等待页面稳定
        except Exception as e:
            print(f"⚠️ 页面加载超时,继续执行: {e}")

        print("✅ 页面加载完成")
    
    async def _wait_for_login(self):
        """等待用户登录"""
        print("\n🔐 请在浏览器中登录抖音...")
        print("   提示: 如果已经登录,请按Enter继续")
        
        # 检查是否已登录
        try:
            # 等待用户头像元素出现(表示已登录)
            await self.page.wait_for_selector(
                'div[class*="avatar"]',
                timeout=60000  # 等待60秒
            )
            print("✅ 检测到登录状态")
        except:
            print("⚠️ 未检测到登录,请手动登录后按Enter继续")
            input("按Enter继续...")
    
    async def _search_keyword(self):
        """执行搜索"""
        print(f"\n🔍 正在搜索关键词: {self.keyword}")

        # 方法1: 直接访问搜索结果页
        search_url = f"https://www.douyin.com/search/{self.keyword}?type=video"
        try:
            await self.page.goto(search_url, timeout=60000)
            await asyncio.sleep(5)  # 等待搜索结果加载
        except Exception as e:
            print(f"⚠️ 搜索页面加载超时,继续执行: {e}")

        # 🔥 新增: 点击"最多点赞"筛选
        await self._click_most_liked_filter()

        print("✅ 搜索完成")

    async def _click_most_liked_filter(self):
        """点击最多点赞筛选按钮"""
        print("\n🎯 正在设置筛选条件: 最多点赞...")

        try:
            # 方法1: 尝试使用你提供的CSS选择器
            filter_selector = "#search-toolbar-container > div.ZyB0s4zV > div > div > div.jjU9T0dQ > span"

            # 等待筛选按钮出现
            try:
                await self.page.wait_for_selector(filter_selector, timeout=5000)
                print("   ✅ 找到筛选按钮(方法1)")
            except:
                # 方法2: 使用更通用的选择器
                print("   ⚠️ 方法1失败,尝试方法2...")
                filter_selector = "span:has-text('综合排序')"
                try:
                    await self.page.wait_for_selector(filter_selector, timeout=5000)
                    print("   ✅ 找到筛选按钮(方法2)")
                except:
                    # 方法3: 使用文本匹配
                    print("   ⚠️ 方法2失败,尝试方法3...")
                    filter_selector = "text=综合排序"
                    try:
                        await self.page.wait_for_selector(filter_selector, timeout=5000)
                        print("   ✅ 找到筛选按钮(方法3)")
                    except:
                        print("   ❌ 未找到筛选按钮,跳过筛选")
                        return

            # 点击筛选按钮
            await self.page.click(filter_selector)
            await asyncio.sleep(1)  # 等待下拉菜单出现
            print("   ✅ 已点击筛选按钮")

            # 点击"最多点赞"选项
            most_liked_selector = "text=最多点赞"
            try:
                await self.page.wait_for_selector(most_liked_selector, timeout=3000)
                await self.page.click(most_liked_selector)
                await asyncio.sleep(2)  # 等待页面重新加载
                print("   ✅ 已选择'最多点赞'排序")
            except:
                print("   ⚠️ 未找到'最多点赞'选项,使用默认排序")

        except Exception as e:
            print(f"   ⚠️ 筛选设置失败: {e}")
            print("   ℹ️ 将使用默认排序继续")
    
    async def _check_captcha(self):
        """🔥 检测是否出现真人验证"""
        try:
            # 检测常见的验证码元素
            captcha_selectors = [
                "text=滑动完成验证",
                "text=点击完成验证",
                "text=拖动滑块",
                "[class*='captcha']",
                "[class*='verify']",
                "[id*='captcha']"
            ]

            for selector in captcha_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        print("\n" + "="*60)
                        print("⚠️  检测到真人验证!")
                        print("="*60)
                        print("请在浏览器中完成验证,然后按Enter继续...")
                        print("="*60)
                        input()
                        print("✅ 继续执行...")
                        return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"⚠️ 验证检测失败: {e}")
            return False

    async def _scroll_and_collect_links(self):
        """滚动页面并收集视频链接"""
        print(f"\n📜 正在收集视频链接 (目标: {self.max_videos}个)...")

        # 🔥 先检查是否有真人验证
        await self._check_captcha()

        collected_count = 0
        scroll_count = 0
        max_scrolls = 50  # 最大滚动次数
        
        while collected_count < self.max_videos and scroll_count < max_scrolls:
            # 提取当前页面的视频链接
            new_links = await self._extract_video_links()
            
            # 添加新链接
            for link in new_links:
                if link not in self.video_links:
                    self.video_links.append(link)
                    collected_count = len(self.video_links)
                    print(f"   ✅ 已收集: {collected_count}/{self.max_videos} - {link}")
                    
                    if collected_count >= self.max_videos:
                        break
            
            # 如果已达到目标数量,退出
            if collected_count >= self.max_videos:
                break
            
            # 滚动页面
            await self.page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(2)  # 等待加载
            scroll_count += 1
            
            print(f"   📜 滚动次数: {scroll_count}, 已收集: {collected_count}")
        
        print(f"\n✅ 收集完成! 共收集 {len(self.video_links)} 个视频链接")
    
    async def _extract_video_links(self) -> List[str]:
        """提取当前页面的视频链接"""
        
        # 方法1: 从搜索结果列表提取
        links = await self.page.evaluate("""
            () => {
                const links = [];
                
                // 查找所有视频链接
                const videoElements = document.querySelectorAll('a[href*="/video/"]');
                
                videoElements.forEach(el => {
                    const href = el.getAttribute('href');
                    if (href && href.includes('/video/')) {
                        // 提取完整链接
                        const fullUrl = href.startsWith('http') 
                            ? href 
                            : 'https://www.douyin.com' + href;
                        links.push(fullUrl);
                    }
                });
                
                return links;
            }
        """)
        
        # 去重并返回
        unique_links = list(set(links))
        return unique_links
    
    def _save_links(self):
        """保存链接到文件"""
        print("\n💾 正在保存视频链接...")
        
        # 创建输出目录
        output_dir = Path("data/douyin/links")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_links_{self.keyword}_{timestamp}.txt"
        filepath = output_dir / filename
        
        # 保存为文本文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# 关键词: {self.keyword}\n")
            f.write(f"# 收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 视频数量: {len(self.video_links)}\n")
            f.write("\n")
            for link in self.video_links:
                f.write(f"{link}\n")
        
        # 保存为JSON格式
        json_filename = f"video_links_{self.keyword}_{timestamp}.json"
        json_filepath = output_dir / json_filename
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "keyword": self.keyword,
                "collect_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "video_count": len(self.video_links),
                "video_links": self.video_links
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 链接已保存:")
        print(f"   📄 文本文件: {filepath}")
        print(f"   📄 JSON文件: {json_filepath}")
        
        # 同时更新到配置文件
        self._update_config()
    
    def _update_config(self):
        """更新配置文件"""
        print("\n⚙️ 正在更新配置文件...")
        
        config_file = Path("config/dy_config.py")
        
        # 读取配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成新的视频列表
        links_str = ",\n    ".join([f'"{link}"' for link in self.video_links[:self.max_videos]])
        new_list = f'DY_SPECIFIED_ID_LIST = [\n    {links_str}\n]'
        
        # 替换配置
        pattern = r'DY_SPECIFIED_ID_LIST\s*=\s*\[.*?\]'
        new_content = re.sub(pattern, new_list, content, flags=re.DOTALL)
        
        # 写回配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 配置文件已更新: {config_file}")
        print(f"   已添加 {len(self.video_links[:self.max_videos])} 个视频链接")
    
    async def _close_browser(self):
        """关闭浏览器"""
        print("\n🔒 正在关闭浏览器...")
        
        if self.browser:
            await self.browser.close()
        
        print("✅ 浏览器已关闭")


async def main():
    """主函数"""
    print("\n" + "🎯" * 30)
    print("RPA模式搜索爬虫 - 混合方案")
    print("🎯" * 30)
    
    # 从配置读取参数
    keyword = base_config.KEYWORDS.split(',')[0].strip()  # 取第一个关键词
    max_videos = base_config.CRAWLER_MAX_NOTES_COUNT
    
    print(f"\n📋 配置信息:")
    print(f"   关键词: {keyword}")
    print(f"   视频数量: {max_videos}")
    
    # 创建爬虫
    crawler = RPASearchCrawler(keyword=keyword, max_videos=max_videos)
    
    # 执行搜索
    video_links = await crawler.start()
    
    # 显示结果
    print("\n" + "=" * 60)
    print("🎉 RPA搜索完成!")
    print("=" * 60)
    print(f"✅ 共收集 {len(video_links)} 个视频链接")
    print("\n📝 下一步:")
    print("   1. 视频链接已自动更新到 config/dy_config.py")
    print("   2. 运行以下命令开始抓取评论:")
    print("      python main.py --platform dy --lt qrcode --type detail")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

