"""
小红书RPA模式搜索爬虫 - 混合方案
功能: 使用RPA模式搜索关键词,获取笔记链接,然后用Detail模式抓取评论
"""

import asyncio
import re
import json
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright, Page, Browser
from datetime import datetime

from config import base_config


class RPAXhsSearchCrawler:
    """小红书RPA模式搜索爬虫"""
    
    def __init__(self, keyword: str, max_notes: int = 20):
        self.keyword = keyword
        self.max_notes = max_notes
        self.note_links = []
        self.browser = None
        self.context = None
        self.page = None
        
    async def start(self):
        """启动爬虫"""
        print("=" * 60)
        print("🚀 小红书RPA模式搜索爬虫启动")
        print("=" * 60)
        print(f"🔍 关键词: {self.keyword}")
        print(f"📝 目标笔记数: {self.max_notes}")
        print("=" * 60)
        
        async with async_playwright() as playwright:
            # 启动浏览器
            await self._launch_browser(playwright)
            
            # 访问小红书搜索页
            await self._goto_search_page()
            
            # 等待用户登录
            await self._wait_for_login()
            
            # 执行搜索
            await self._search_keyword()
            
            # 滚动加载笔记
            await self._scroll_and_collect_links()
            
            # 保存链接
            self._save_links()
            
            # 关闭浏览器
            await self._close_browser()
            
        return self.note_links
    
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
        """访问小红书搜索页"""
        print("\n🌐 正在访问小红书搜索页...")

        url = "https://www.xiaohongshu.com/"
        try:
            await self.page.goto(url, timeout=60000)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"⚠️ 页面加载超时,继续执行: {e}")

        print("✅ 页面加载完成")
    
    async def _wait_for_login(self):
        """等待用户登录"""
        print("\n🔐 请在浏览器中登录小红书...")
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
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={self.keyword}"
        try:
            await self.page.goto(search_url, timeout=60000)
            await asyncio.sleep(5)  # 等待搜索结果加载
        except Exception as e:
            print(f"⚠️ 搜索页面加载超时,继续执行: {e}")

        # 🔥 新增: 点击"最多评论"筛选
        await self._click_most_comments_filter()

        print("✅ 搜索完成")

    async def _click_most_comments_filter(self):
        """点击最多评论筛选按钮"""
        print("\n🎯 正在设置筛选条件: 最多评论...")

        try:
            # 🔥 第1步: 点击"筛选"按钮
            print("   📍 步骤1: 查找并点击'筛选'按钮...")
            
            filter_selectors = [
                # 方法1: XPath(最稳定)
                "//span[contains(text(),'筛选')]",
                # 方法2: 用户提供的XPath
                "(//span[contains(text(),'筛选')])[1]",
                # 方法3: 用户提供的CSS选择器
                "body > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > span:nth-child(1)",
                # 方法4: 通用文本匹配
                "text=筛选",
                # 方法5: 包含文本的span
                "span:has-text('筛选')",
                # 方法6: 简化的CSS
                "div.filter > span"
            ]

            filter_clicked = False
            for idx, selector in enumerate(filter_selectors, 1):
                try:
                    print(f"      尝试方法{idx}: {selector[:50]}...")
                    filter_element = await self.page.wait_for_selector(selector, timeout=3000)
                    # 🔥 关键修改: 使用hover()而不是click()
                    await filter_element.hover()
                    await asyncio.sleep(1.5)  # 等待下拉菜单出现(增加等待时间)
                    print(f"      ✅ 方法{idx}成功! 已悬停在'筛选'按钮上")
                    filter_clicked = True
                    break
                except Exception as e:
                    print(f"      ❌ 方法{idx}失败: {str(e)[:50]}")
                    continue

            if not filter_clicked:
                print("   ⚠️ 未找到'筛选'按钮,跳过筛选,使用默认排序")
                return

            # 🔥 第2步: 点击"最多评论"选项
            print("   📍 步骤2: 查找并点击'最多评论'选项...")
            
            most_comments_selectors = [
                # 方法1: 测试中成功率最高的选择器
                "div[class*='filter'] span:has-text('最多评论')",
                # 方法2: XPath
                "//span[contains(text(),'最多评论')]",
                # 方法3: 用户提供的XPath
                "(//span[contains(text(),'最多评论')])[1]",
                # 方法4: 通用文本匹配
                "text=最多评论",
                # 方法5: 包含文本的span
                "span:has-text('最多评论')",
                # 方法6: 备用CSS
                "div[class*='sort'] span:has-text('最多评论')"
            ]

            comments_clicked = False
            for idx, selector in enumerate(most_comments_selectors, 1):
                try:
                    print(f"      尝试方法{idx}: {selector[:50]}...")
                    await self.page.wait_for_selector(selector, timeout=3000)
                    await self.page.click(selector)
                    await asyncio.sleep(2)  # 等待页面重新加载
                    print(f"      ✅ 方法{idx}成功! 已选择'最多评论'排序")
                    comments_clicked = True
                    break
                except Exception as e:
                    print(f"      ❌ 方法{idx}失败: {str(e)[:50]}")
                    continue

            if not comments_clicked:
                print("   ⚠️ 未找到'最多评论'选项,使用默认排序")
            else:
                print("   🎉 筛选设置成功!")

                # 🔥 关键修复: 点击空白处关闭筛选面板
                print("   📍 步骤3: 关闭筛选面板...")
                try:
                    # 方法1: 按ESC键关闭
                    await self.page.keyboard.press('Escape')
                    await asyncio.sleep(0.5)
                    print("      ✅ 已按ESC键关闭筛选面板")
                except Exception as e:
                    print(f"      ⚠️ 按ESC键失败: {str(e)[:50]}")
                    try:
                        # 方法2: 点击页面空白处
                        await self.page.click('body', position={'x': 100, 'y': 100})
                        await asyncio.sleep(0.5)
                        print("      ✅ 已点击空白处关闭筛选面板")
                    except Exception as e2:
                        print(f"      ⚠️ 点击空白处失败: {str(e2)[:50]}")

        except Exception as e:
            print(f"   ⚠️ 筛选设置失败: {e}")
            print("   ℹ️ 将使用默认排序继续")
    
    async def _scroll_and_collect_links(self):
        """
        🔥 完全模拟真实用户行为:
        1. 滚动浏览搜索结果,确保有足够的笔记卡片可见
        2. 不收集note_id,而是准备好笔记卡片供后续点击
        """
        print(f"\n📜 开始模拟真实用户浏览...")
        print(f"   目标: {self.max_notes} 个笔记")

        # 🔥 滚动页面,确保有足够的笔记卡片加载出来
        scroll_count = 0
        max_scrolls = 10  # 减少滚动次数,只需要确保有足够的卡片即可

        print(f"\n📜 滚动页面,加载笔记卡片...")
        while scroll_count < max_scrolls:
            # 获取当前页面的笔记卡片数量
            note_cards = await self.page.query_selector_all('a[href*="/explore/"]')
            current_count = len(note_cards)

            print(f"   📜 滚动次数: {scroll_count + 1}, 当前可见: {current_count} 个笔记")

            # 如果已经有足够的笔记卡片,停止滚动
            if current_count >= self.max_notes * 2:  # 多加载一些,以防有些卡片无效
                print(f"   ✅ 已加载足够的笔记卡片,停止滚动")
                break

            # 滚动页面
            await self.page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1.5)
            scroll_count += 1

        print(f"\n✅ 页面准备完成! 准备从左到右依次点击笔记...")

        # 🔥 不再收集note_id,而是标记准备好了
        self.note_links = []  # 清空,不使用链接模式
        self.ready_to_click = True  # 标记准备好点击
    async def click_and_scrape_notes(self, xhs_client) -> List[Dict]:
        """
        🔥 完全模拟真实用户: 从左到右依次点击笔记卡片 → 浏览详情 → 抓取评论 → 返回搜索页

        Args:
            xhs_client: 小红书客户端,用于API调用

        Returns:
            笔记数据列表
        """
        import random

        if not hasattr(self, 'ready_to_click') or not self.ready_to_click:
            print("   ⚠️ 页面未准备好")
            return []

        all_notes_data = []

        print(f"\n🔥 开始模拟真实用户: 从左到右依次点击笔记...")
        print(f"📊 目标: {self.max_notes} 个笔记")
        print(f"⏰ 每个笔记之间延迟 30-45 秒,模拟真实用户行为")

        # 保存搜索页URL
        search_url = self.page.url

        # 🔥 核心改进: 逐个点击卡片,而不是导航到URL
        clicked_count = 0

        while clicked_count < self.max_notes:
            try:
                print(f"\n{'='*60}")
                print(f"📝 [{clicked_count + 1}/{self.max_notes}] 准备点击第 {clicked_count + 1} 个笔记")
                print(f"{'='*60}")

                # 🔥 步骤1: 获取当前页面的所有笔记卡片
                print(f"   🔍 查找笔记卡片...")
                note_cards = await self.page.query_selector_all('a[href*="/explore/"]')

                if not note_cards or len(note_cards) <= clicked_count:
                    print(f"   ⚠️ 没有更多笔记卡片了")
                    break

                # 🔥 步骤2: 获取第N个卡片(从左到右,从上到下的顺序)
                target_card = note_cards[clicked_count]

                # 获取note_id用于日志
                href = await target_card.get_attribute('href')
                note_id = href.split('/explore/')[1].split('?')[0] if href and '/explore/' in href else 'unknown'

                print(f"   🎯 目标笔记: {note_id}")

                # 🔥 步骤3: 滚动到卡片可见区域
                print(f"   📜 滚动到笔记卡片...")
                await target_card.scroll_into_view_if_needed(timeout=5000)
                await asyncio.sleep(random.uniform(0.5, 1))

                # 🔥 步骤4: 点击卡片(模拟真实用户点击)
                print(f"   👆 点击笔记卡片...")
                try:
                    # 尝试普通点击
                    await target_card.click(timeout=5000)
                except Exception as e:
                    print(f"   ⚠️ 普通点击失败,尝试强制点击: {str(e)[:50]}")
                    # 如果普通点击失败,使用JavaScript点击
                    await target_card.evaluate('element => element.click()')

                # 🔥 步骤5: 等待页面跳转到详情页
                print(f"   ⏳ 等待页面跳转...")
                await asyncio.sleep(random.uniform(2, 3))

                # 🔥 步骤6: 从地址栏获取完整URL(包含xsec参数)
                current_url = self.page.url

                # 检查是否成功跳转到详情页
                if '/explore/' not in current_url or '/404' in current_url:
                    print(f"   ❌ 页面跳转失败或被重定向到404")
                    print(f"   🔗 当前URL: {current_url[:80]}...")
                    # 返回搜索页
                    await self.page.go_back(wait_until='domcontentloaded', timeout=10000)
                    await asyncio.sleep(2)
                    clicked_count += 1
                    continue

                # 解析URL获取xsec参数
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(current_url)
                query_params = parse_qs(parsed.query)
                xsec_token = query_params.get('xsec_token', [''])[0]
                xsec_source = query_params.get('xsec_source', [''])[0]

                print(f"   ✅ 成功进入笔记详情页")
                print(f"   🔗 完整URL: {current_url[:80]}...")
                print(f"   🔑 xsec_token: {xsec_token[:20]}..." if xsec_token else "   ⚠️ 缺少xsec_token")

                # 模拟真实用户浏览笔记
                browse_delay = random.uniform(3, 5)
                print(f"   👀 浏览笔记内容 ({browse_delay:.1f}秒)...")
                await asyncio.sleep(browse_delay)

                # 🔥 步骤7: 抓取笔记详情
                print(f"   📄 正在获取笔记详情...")
                note_detail = await xhs_client.get_note_by_id_from_html(current_url)

                if not note_detail:
                    print(f"   ❌ 笔记详情获取失败")
                    # 返回搜索页
                    await self.page.go_back(wait_until='domcontentloaded', timeout=10000)
                    await asyncio.sleep(2)
                    clicked_count += 1
                    continue

                print(f"   ✅ 笔记详情获取成功")
                print(f"   📝 标题: {note_detail.get('title', 'N/A')[:30]}...")
                print(f"   👤 作者: {note_detail.get('nickname', 'N/A')}")

                # 🔥 步骤8: 滚动页面,模拟查看评论
                print(f"   📜 滚动查看评论区...")
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(random.uniform(2, 3))

                # 🔥 步骤9: 抓取评论
                print(f"   💬 正在获取评论...")
                comments = await xhs_client.get_note_comments(
                    note_id=note_id,
                    xsec_token=xsec_token,
                    xsec_source=xsec_source
                )

                if comments:
                    print(f"   ✅ 成功获取 {len(comments)} 条评论")
                else:
                    print(f"   ⚠️ 未获取到评论")

                # 保存数据
                note_data = {
                    'note_id': note_id,
                    'note_url': current_url,
                    'note_detail': note_detail,
                    'comments': comments or []
                }
                all_notes_data.append(note_data)

                # 🔥 步骤10: 返回搜索页(使用浏览器后退按钮)
                if clicked_count < self.max_notes - 1:  # 不是最后一个
                    # 模拟真实用户返回
                    return_delay = random.uniform(30, 45)
                    print(f"   ⏰ 等待 {return_delay:.1f} 秒后返回搜索页...")
                    await asyncio.sleep(return_delay)

                    print(f"   ↩️ 点击浏览器后退按钮...")
                    await self.page.go_back(wait_until='domcontentloaded', timeout=10000)
                    await asyncio.sleep(random.uniform(2, 3))

                    print(f"   ✅ 已返回搜索页,准备点击下一个笔记")

                clicked_count += 1

            except Exception as e:
                print(f"   ❌ 处理失败: {str(e)[:100]}")
                # 尝试返回搜索页
                try:
                    print(f"   ↩️ 尝试返回搜索页...")
                    await self.page.go_back(wait_until='domcontentloaded', timeout=10000)
                    await asyncio.sleep(2)
                except:
                    # 如果后退失败,直接导航到搜索页
                    try:
                        await self.page.goto(search_url, wait_until='domcontentloaded', timeout=10000)
                        await asyncio.sleep(2)
                    except:
                        pass
                clicked_count += 1
                continue

        print(f"\n{'='*60}")
        print(f"🎉 所有笔记处理完成!")
        print(f"✅ 成功: {len(all_notes_data)}/{self.max_notes} 个笔记")
        print(f"{'='*60}")

        return all_notes_data

    async def _extract_note_links_by_clicking(self, note_ids: List[str]) -> List[str]:
        """
        通过点击笔记卡片获取完整URL(包含xsec_token和xsec_source)

        Args:
            note_ids: 要获取完整URL的note_id列表

        Returns:
            包含完整参数的URL列表
        """
        import random

        links = []
        processed_note_ids = set()

        print(f"   需要获取 {len(note_ids)} 个笔记的完整链接")

        # 🔥 逐个点击获取完整URL
        for index, target_note_id in enumerate(note_ids, 1):
            if target_note_id in processed_note_ids:
                continue

            try:
                # 🔥 每次都重新获取元素
                note_cards = await self.page.query_selector_all('a[href*="/explore/"]')

                # 找到目标note_id的卡片
                target_card = None
                for card in note_cards:
                    try:
                        href = await card.get_attribute('href')
                        if href and target_note_id in href:
                            target_card = card
                            break
                    except:
                        continue

                if not target_card:
                    print(f"   ⚠️ [{index}/{len(note_ids)}] 未找到笔记 {target_note_id} 的卡片")
                    continue

                # 🔥 滚动到元素可见
                try:
                    await target_card.scroll_into_view_if_needed(timeout=5000)
                    await asyncio.sleep(0.5)
                except:
                    pass

                # 🔥 尝试点击(使用force=True强制点击)
                try:
                    await target_card.click(timeout=10000, force=True)
                except Exception as click_error:
                    # 如果普通点击失败,尝试JavaScript点击
                    try:
                        await target_card.evaluate('element => element.click()')
                    except:
                        print(f"   ❌ [{index}/{len(note_ids)}] 点击失败: {str(click_error)[:40]}")
                        continue

                # 等待页面跳转
                delay = random.uniform(2, 3)
                await asyncio.sleep(delay)

                # 获取完整URL
                full_url = self.page.url

                # 验证URL
                if '/explore/' in full_url and 'xsec_token=' in full_url and 'xsec_source=' in full_url:
                    links.append(full_url)
                    processed_note_ids.add(target_note_id)
                    print(f"   ✅ [{index}/{len(note_ids)}] 已获取: {target_note_id}")
                else:
                    print(f"   ⚠️ [{index}/{len(note_ids)}] URL缺少参数: {full_url[:60]}")

                # 返回搜索页
                await self.page.go_back()

                # 等待页面加载
                delay = random.uniform(1.5, 2.5)
                await asyncio.sleep(delay)

            except Exception as e:
                print(f"   ❌ [{index}/{len(note_ids)}] 获取失败: {str(e)[:40]}")
                # 尝试返回搜索页
                try:
                    current_url = self.page.url
                    if '/explore/' in current_url:
                        await self.page.go_back()
                        await asyncio.sleep(1)
                except:
                    pass
                continue

        return links
    
    def _save_links(self):
        """保存链接到配置文件"""
        print(f"\n💾 正在保存链接到配置文件...")
        
        # 保存到 config/xhs_config.py
        config_file = Path(__file__).parent / "config" / "xhs_config.py"
        
        try:
            # 读取现有配置
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 构建新的链接列表
            links_str = '[\n'
            for link in self.note_links:
                links_str += f'    "{link}",\n'
            links_str += ']'
            
            # 替换 XHS_SPECIFIED_NOTE_URL_LIST
            import re
            pattern = r'XHS_SPECIFIED_NOTE_URL_LIST\s*=\s*\[.*?\]'
            replacement = f'XHS_SPECIFIED_NOTE_URL_LIST = {links_str}'
            
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # 写回文件
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已保存 {len(self.note_links)} 个链接到 {config_file}")
            
        except Exception as e:
            print(f"⚠️ 保存链接失败: {e}")
            print("   链接列表:")
            for link in self.note_links:
                print(f"   - {link}")
    
    async def _close_browser(self):
        """关闭浏览器"""
        print("\n🔒 正在关闭浏览器...")
        
        if self.browser:
            await self.browser.close()
        
        print("✅ 浏览器已关闭")


async def main():
    """主函数"""
    print("\n" + "🎯" * 30)
    print("小红书RPA模式搜索爬虫 - 混合方案")
    print("🎯" * 30)
    
    # 从配置读取参数
    keyword = base_config.KEYWORDS.split(',')[0].strip()  # 取第一个关键词
    max_notes = base_config.CRAWLER_MAX_NOTES_COUNT
    
    print(f"\n📋 配置信息:")
    print(f"   关键词: {keyword}")
    print(f"   笔记数量: {max_notes}")
    
    # 创建爬虫
    crawler = RPAXhsSearchCrawler(keyword=keyword, max_notes=max_notes)
    
    # 执行搜索
    note_links = await crawler.start()
    
    # 显示结果
    print("\n" + "=" * 60)
    print("🎉 RPA搜索完成!")
    print("=" * 60)
    print(f"✅ 共收集 {len(note_links)} 个笔记链接")
    print("\n📝 下一步:")
    print("   1. 笔记链接已自动更新到 config/xhs_config.py")
    print("   2. 运行以下命令开始抓取评论:")
    print("      python main.py --platform xhs --lt qrcode --type detail")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

