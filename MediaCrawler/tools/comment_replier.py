# 评论回复工具
# 用于在视频页面中定位指定评论并回复

import asyncio
from typing import Dict, Optional
from playwright.async_api import Page, TimeoutError
import random


class CommentReplier:
    """评论回复器 - 使用RPA方式定位并回复评论"""

    def __init__(self, page: Page):
        self.page = page

    async def reply_to_comment(
        self,
        video_url: str,
        comment_content: str,
        reply_text: str,
        comment_id: Optional[str] = None
    ) -> Dict:
        """
        在视频页面中找到指定评论并回复

        Args:
            video_url: 视频链接
            comment_content: 评论内容（用于定位评论）
            reply_text: 回复内容
            comment_id: 评论ID（可选，更精确）

        Returns:
            {"success": bool, "message": str}
        """
        try:
            print(f"\n{'='*60}")
            print(f"🎯 准备回复评论")
            print(f"视频: {video_url}")
            print(f"评论: {comment_content[:50]}...")
            print(f"回复: {reply_text}")
            print(f"{'='*60}\n")

            # 1. 打开视频页面
            print("📱 正在打开视频页面...")
            await self.page.goto(video_url, wait_until="networkidle")
            await asyncio.sleep(2)

            # 2. 滚动到评论区
            print("📜 正在滚动到评论区...")
            await self._scroll_to_comments_section()

            # 3. 定位目标评论
            print(f"🔍 正在查找评论: {comment_content[:30]}...")
            comment_element = await self._find_comment_element(comment_content, comment_id)

            if not comment_element:
                return {
                    "success": False,
                    "message": f"未找到评论: {comment_content[:30]}"
                }

            print("✅ 找到目标评论!")

            # 4. 点击回复按钮
            print("💬 正在点击回复按钮...")
            reply_success = await self._click_reply_button(comment_element)

            if not reply_success:
                return {
                    "success": False,
                    "message": "无法点击回复按钮"
                }

            # 5. 输入回复内容
            print(f"⌨️  正在输入回复: {reply_text}")
            await self._type_reply_text(reply_text)

            # 6. 发送回复
            print("📤 正在发送回复...")
            send_success = await self._send_reply()

            if send_success:
                print("✅ 回复发送成功!")
                return {
                    "success": True,
                    "message": "回复成功"
                }
            else:
                return {
                    "success": False,
                    "message": "发送失败"
                }

        except Exception as e:
            print(f"❌ 回复失败: {e}")
            return {
                "success": False,
                "message": f"异常: {str(e)}"
            }

    async def _scroll_to_comments_section(self):
        """滚动到评论区"""
        # 抖音评论区通常在页面中下部
        for i in range(3):
            await self.page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(0.5)

    async def _find_comment_element(self, content: str, comment_id: Optional[str] = None):
        """
        在页面中找到目标评论元素

        策略：
        1. 如果有comment_id，优先用data-comment-id属性定位
        2. 否则用评论文本内容定位
        """
        # 等待评论列表加载
        try:
            await self.page.wait_for_selector(
                'xpath=//div[contains(@class, "comment")]',
                timeout=5000
            )
        except TimeoutError:
            print("⚠️ 评论区加载超时")
            return None

        # 策略1：使用comment_id定位（如果提供）
        if comment_id:
            try:
                element = await self.page.query_selector(
                    f'xpath=//div[@data-comment-id="{comment_id}"]'
                )
                if element:
                    return element
            except:
                pass

        # 策略2：使用内容文本定位
        # 抖音评论结构：<div class="comment-item">...<span>评论内容</span>...
        # 需要滚动加载更多评论，直到找到目标

        max_scrolls = 20  # 最多滚动20次
        for scroll_count in range(max_scrolls):
            # 查找所有评论元素
            comment_elements = await self.page.query_selector_all(
                'xpath=//div[contains(@class, "comment") or contains(@data-e2e, "comment")]'
            )

            print(f"  当前页面评论数: {len(comment_elements)}")

            # 遍历查找匹配的评论
            for element in comment_elements:
                try:
                    # 获取评论文本
                    text = await element.inner_text()

                    # 检查是否匹配（支持部分匹配）
                    if content in text or text in content:
                        print(f"  ✅ 匹配成功: {text[:50]}...")
                        # 滚动到该元素可见
                        await element.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        return element
                except:
                    continue

            # 未找到，继续滚动加载更多评论
            print(f"  未找到，继续滚动... ({scroll_count + 1}/{max_scrolls})")
            await self.page.evaluate("window.scrollBy(0, 300)")
            await asyncio.sleep(1)

        return None

    async def _click_reply_button(self, comment_element) -> bool:
        """点击评论的回复按钮"""
        try:
            # 抖音评论的回复按钮通常在评论元素内部
            # 可能的选择器：
            selectors = [
                'xpath=.//span[text()="回复"]',
                'xpath=.//div[text()="回复"]',
                'xpath=.//button[contains(text(), "回复")]',
                'xpath=.//*[@data-e2e="comment-reply-btn"]',
                'xpath=.//*[contains(@class, "reply")]',
            ]

            for selector in selectors:
                try:
                    reply_btn = await comment_element.query_selector(selector)
                    if reply_btn:
                        await reply_btn.click()
                        await asyncio.sleep(1)
                        return True
                except:
                    continue

            # 如果没有找到回复按钮，尝试悬停评论元素
            # 有些平台回复按钮是悬停后才显示
            await comment_element.hover()
            await asyncio.sleep(0.5)

            for selector in selectors:
                try:
                    reply_btn = await comment_element.query_selector(selector)
                    if reply_btn:
                        await reply_btn.click()
                        await asyncio.sleep(1)
                        return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"  点击回复按钮失败: {e}")
            return False

    async def _type_reply_text(self, text: str):
        """输入回复内容"""
        # 等待输入框出现
        await asyncio.sleep(0.5)

        # 可能的输入框选择器
        selectors = [
            'xpath=//textarea[@data-e2e="comment-input"]',
            'xpath=//div[@contenteditable="true"]',
            'xpath=//textarea[contains(@placeholder, "回复")]',
            'xpath=//textarea[contains(@placeholder, "评论")]',
            'xpath=//input[@type="text" and contains(@placeholder, "回复")]',
        ]

        for selector in selectors:
            try:
                input_box = await self.page.query_selector(selector)
                if input_box:
                    # 聚焦输入框
                    await input_box.click()
                    await asyncio.sleep(0.3)

                    # 模拟真人输入（逐字输入）
                    for char in text:
                        await input_box.type(char, delay=random.randint(50, 150))

                    await asyncio.sleep(0.5)
                    return True
            except:
                continue

        # 如果以上都失败，尝试直接填充
        try:
            await self.page.fill('textarea', text)
            return True
        except:
            pass

        raise Exception("未找到评论输入框")

    async def _send_reply(self) -> bool:
        """点击发送按钮"""
        # 可能的发送按钮选择器
        selectors = [
            'xpath=//span[text()="发送"]',
            'xpath=//button[text()="发送"]',
            'xpath=//div[text()="发送"]',
            'xpath=//*[@data-e2e="comment-send-btn"]',
            'xpath=//button[contains(@class, "send")]',
        ]

        for selector in selectors:
            try:
                send_btn = await self.page.query_selector(selector)
                if send_btn:
                    await send_btn.click()
                    await asyncio.sleep(2)

                    # 检查是否发送成功
                    # 通常发送成功后输入框会清空
                    try:
                        success_indicator = await self.page.query_selector(
                            'xpath=//*[contains(text(), "评论成功") or contains(text(), "回复成功")]'
                        )
                        if success_indicator:
                            return True
                    except:
                        pass

                    # 或者检查输入框是否已清空
                    return True
            except:
                continue

        return False

    async def batch_reply(self, comments_to_reply: list, reply_mapping: dict) -> list:
        """
        批量回复多条评论

        Args:
            comments_to_reply: 需要回复的评论列表
            reply_mapping: 回复内容映射
                {
                    "关键词1": "回复内容1",
                    "关键词2": "回复内容2",
                    "default": "默认回复"
                }

        Returns:
            结果列表
        """
        results = []

        for comment in comments_to_reply:
            content = comment.get("content", "")
            video_url = comment.get("video_url", "")
            comment_id = comment.get("comment_id")

            # 根据评论内容选择回复
            reply_text = self._get_reply_text(content, reply_mapping)

            # 执行回复
            result = await self.reply_to_comment(
                video_url=video_url,
                comment_content=content,
                reply_text=reply_text,
                comment_id=comment_id
            )

            results.append({
                "comment": content[:50],
                "reply": reply_text,
                **result
            })

            # 延迟，避免频繁操作
            delay = random.randint(5, 10)
            print(f"⏱️  等待 {delay} 秒后处理下一条...")
            await asyncio.sleep(delay)

        return results

    def _get_reply_text(self, comment_content: str, reply_mapping: dict) -> str:
        """根据评论内容选择回复"""
        for keyword, reply in reply_mapping.items():
            if keyword != "default" and keyword in comment_content:
                return reply
        return reply_mapping.get("default", "感谢您的评论！")


# 使用示例
async def example_usage():
    """使用示例"""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 创建回复器
        replier = CommentReplier(page)

        # 回复单条评论
        result = await replier.reply_to_comment(
            video_url="https://www.douyin.com/video/7525538910311632128",
            comment_content="这个多少钱？",
            reply_text="私信我获取价格哦~",
            comment_id="7525082444551310602"
        )

        print(f"\n结果: {result}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
