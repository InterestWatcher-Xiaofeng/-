"""
tkinterweb浏览器内嵌模块
使用tkinterweb实现浏览器内嵌功能
支持Python 3.12，原生Tkinter组件
"""

import tkinter as tk
from tkinterweb import HtmlFrame
import customtkinter as ctk


class TkinterWebBrowser:
    """tkinterweb浏览器封装类"""

    def __init__(self, parent_frame):
        """
        初始化tkinterweb浏览器

        Args:
            parent_frame: 父容器Frame
        """
        self.parent_frame = parent_frame
        self.html_frame = None
        self.current_url = "about:blank"
        self.is_ready = False

    def create_window(self, title="浏览器", width=800, height=600, x=None, y=None):
        """
        创建浏览器窗口

        Args:
            title: 窗口标题
            width: 窗口宽度
            height: 窗口高度
            x: 窗口X坐标
            y: 窗口Y坐标
        """
        # 欢迎HTML
        welcome_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }
                .container {
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    text-align: center;
                }
                h1 {
                    color: #667eea;
                    font-size: 36px;
                    margin-bottom: 15px;
                }
                .status {
                    color: #4CAF50;
                    font-size: 20px;
                    margin: 20px 0;
                }
                .info {
                    color: #666;
                    font-size: 16px;
                    line-height: 1.8;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🍁 红枫工具箱</h1>
                <div class="status">✅ 浏览器已就绪</div>
                <div class="info">
                    <p>🌐 pywebview内嵌浏览器</p>
                    <p>✅ 支持Python 3.12</p>
                    <p>🚀 基于Edge WebView2</p>
                </div>
            </div>
        </body>
        </html>
        """

        # 在新线程中创建窗口
        def start_webview():
            self.window = self.webview.create_window(
                title=title,
                html=welcome_html,
                width=width,
                height=height,
                x=x,
                y=y,
                resizable=True,
                frameless=False
            )
            self.webview.start()
            self.is_ready = True

        thread = threading.Thread(target=start_webview, daemon=True)
        thread.start()

        # 等待窗口创建
        time.sleep(0.5)

        return self.window

    def load_url(self, url: str):
        """加载URL"""
        if self.window:
            self.window.load_url(url)
            self.current_url = url

    def load_html(self, html: str):
        """加载HTML内容"""
        if self.window:
            self.window.load_html(html)

    def get_url(self) -> str:
        """获取当前URL"""
        return self.current_url

    def destroy(self):
        """销毁窗口"""
        if self.window:
            self.window.destroy()


class WebViewBrowserManager:
    """pywebview浏览器管理器（单例模式）"""

    _instance = None
    _browser = None

    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """初始化管理器"""
        if WebViewBrowserManager._instance is not None:
            raise Exception("WebViewBrowserManager是单例类，请使用get_instance()获取实例")

        self.initialized = False

    def initialize(self, title="浏览器预览", width=700, height=750, x=None, y=None):
        """
        初始化pywebview浏览器

        Args:
            title: 窗口标题
            width: 窗口宽度
            height: 窗口高度
            x: 窗口X坐标
            y: 窗口Y坐标
        """
        if self.initialized:
            return True

        try:
            WebViewBrowserManager._browser = WebViewBrowser()
            WebViewBrowserManager._browser.create_window(
                title=title,
                width=width,
                height=height,
                x=x,
                y=y
            )

            self.initialized = True
            print("✅ pywebview浏览器初始化成功")
            return True

        except Exception as e:
            print(f"❌ pywebview浏览器初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_url(self, url: str):
        """加载URL"""
        if WebViewBrowserManager._browser:
            WebViewBrowserManager._browser.load_url(url)

    def load_html(self, html: str):
        """加载HTML"""
        if WebViewBrowserManager._browser:
            WebViewBrowserManager._browser.load_html(html)

    def get_url(self) -> str:
        """获取当前URL"""
        if WebViewBrowserManager._browser:
            return WebViewBrowserManager._browser.get_url()
        return ""

    def shutdown(self):
        """关闭浏览器"""
        if WebViewBrowserManager._browser:
            WebViewBrowserManager._browser.destroy()
            WebViewBrowserManager._browser = None

        self.initialized = False
        print("✅ pywebview浏览器已关闭")


# 测试代码
if __name__ == "__main__":
    print("🧪 测试pywebview浏览器...")

    manager = WebViewBrowserManager.get_instance()
    manager.initialize(title="pywebview测试", width=1000, height=700)

    print("✅ 浏览器窗口已创建")
    print("💡 关闭浏览器窗口即可退出测试")

