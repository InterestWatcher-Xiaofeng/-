"""
tkinterweb浏览器内嵌模块
使用tkinterweb实现浏览器内嵌功能
支持Python 3.12，原生Tkinter组件，跨平台兼容
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

    def create_widget(self):
        """创建浏览器组件"""
        try:
            # 创建HtmlFrame
            self.html_frame = HtmlFrame(self.parent_frame, messages_enabled=False)
            self.html_frame.pack(fill="both", expand=True)
            
            # 加载欢迎页面
            welcome_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {
                        margin: 0;
                        padding: 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        font-family: 'Microsoft YaHei', Arial, sans-serif;
                        color: white;
                        text-align: center;
                    }
                    .container {
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 10px;
                        padding: 30px;
                        margin-top: 50px;
                    }
                    h1 {
                        font-size: 28px;
                        margin-bottom: 15px;
                    }
                    .status {
                        color: #90EE90;
                        font-size: 18px;
                        margin: 15px 0;
                        font-weight: bold;
                    }
                    p {
                        font-size: 14px;
                        opacity: 0.9;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🍁 红枫工具箱</h1>
                    <div class="status">✅ 浏览器预览已就绪</div>
                    <p>登录时将同步显示浏览器内容</p>
                    <p>原生Tkinter组件 · 跨平台兼容</p>
                </div>
            </body>
            </html>
            """
            
            self.html_frame.load_html(welcome_html)
            self.is_ready = True
            
            return self.html_frame
            
        except Exception as e:
            print(f"❌ 创建浏览器组件失败: {e}")
            return None

    def load_url(self, url: str):
        """加载URL"""
        if self.html_frame:
            try:
                self.html_frame.load_url(url)
                self.current_url = url
            except Exception as e:
                print(f"❌ 加载URL失败: {e}")

    def load_html(self, html: str):
        """加载HTML内容"""
        if self.html_frame:
            try:
                self.html_frame.load_html(html)
            except Exception as e:
                print(f"❌ 加载HTML失败: {e}")

    def show_crawling_progress(self, platform: str, keyword: str, current: int, total: int, status: str = "进行中", error: str = ""):
        """显示采集进度"""
        platform_names = {
            "dy": "抖音",
            "xhs": "小红书",
            "bili": "B站",
            "zhihu": "知乎"
        }
        platform_name = platform_names.get(platform, platform)

        # 计算进度百分比
        progress_percent = int((current / total * 100)) if total > 0 else 0

        # 状态颜色
        status_colors = {
            "进行中": "#4CAF50",
            "完成": "#2196F3",
            "错误": "#F44336",
            "暂停": "#FF9800"
        }
        status_color = status_colors.get(status, "#4CAF50")

        # 生成进度HTML
        progress_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    color: white;
                }}
                .container {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 30px;
                    backdrop-filter: blur(10px);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .platform {{
                    font-size: 32px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .keyword {{
                    font-size: 24px;
                    color: #FFD700;
                    margin-bottom: 20px;
                }}
                .progress-section {{
                    margin: 20px 0;
                }}
                .progress-label {{
                    font-size: 16px;
                    margin-bottom: 10px;
                    display: flex;
                    justify-content: space-between;
                }}
                .progress-bar-container {{
                    width: 100%;
                    height: 30px;
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 15px;
                    overflow: hidden;
                    position: relative;
                }}
                .progress-bar {{
                    height: 100%;
                    background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
                    border-radius: 15px;
                    transition: width 0.3s ease;
                    width: {progress_percent}%;
                }}
                .progress-text {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    text-shadow: 0 0 5px rgba(0,0,0,0.5);
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-top: 20px;
                }}
                .stat-item {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                }}
                .stat-value {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #FFD700;
                }}
                .stat-label {{
                    font-size: 14px;
                    margin-top: 5px;
                    opacity: 0.9;
                }}
                .status {{
                    text-align: center;
                    margin-top: 20px;
                    padding: 15px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    border-left: 5px solid {status_color};
                }}
                .status-text {{
                    font-size: 18px;
                    font-weight: bold;
                    color: {status_color};
                }}
                .error {{
                    margin-top: 15px;
                    padding: 15px;
                    background: rgba(244, 67, 54, 0.2);
                    border-radius: 10px;
                    border-left: 5px solid #F44336;
                    color: #FFB3B3;
                }}
                .spinner {{
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    border: 3px solid rgba(255,255,255,.3);
                    border-radius: 50%;
                    border-top-color: #fff;
                    animation: spin 1s ease-in-out infinite;
                }}
                @keyframes spin {{
                    to {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="platform">🎯 {platform_name} 数据采集</div>
                    <div class="keyword">📝 {keyword}</div>
                </div>

                <div class="progress-section">
                    <div class="progress-label">
                        <span>采集进度</span>
                        <span>{current} / {total}</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar"></div>
                        <div class="progress-text">{progress_percent}%</div>
                    </div>
                </div>

                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-value">{current}</div>
                        <div class="stat-label">已采集</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{total - current}</div>
                        <div class="stat-label">剩余</div>
                    </div>
                </div>

                <div class="status">
                    <div class="status-text">
                        {"<span class='spinner'></span>" if status == "进行中" else ""}
                        {status}
                    </div>
                </div>

                {f'<div class="error">❌ {error}</div>' if error else ''}
            </div>
        </body>
        </html>
        """

        self.load_html(progress_html)

    def show_crawling_progress_v2(self, platform: str, keyword: str, current: int, total: int, status: str = "进行中", error: str = ""):
        """显示采集进度 - 美化版V2"""
        platform_names = {"dy": "抖音", "xhs": "小红书", "bili": "B站", "zhihu": "知乎"}
        platform_name = platform_names.get(platform, platform)

        platform_icons = {"dy": "🎵", "xhs": "📕", "bili": "📺", "zhihu": "🔍"}
        platform_icon = platform_icons.get(platform, "🎯")

        progress_percent = int((current / total * 100)) if total > 0 else 0

        status_config = {
            "进行中": {"color": "#4CAF50", "bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", "icon": "⚡", "spinner": True},
            "完成": {"color": "#2196F3", "bg": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)", "icon": "✅", "spinner": False},
            "错误": {"color": "#F44336", "bg": "linear-gradient(135deg, #eb3349 0%, #f45c43 100%)", "icon": "❌", "spinner": False},
            "暂停": {"color": "#FF9800", "bg": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)", "icon": "⏸️", "spinner": False}
        }

        config = status_config.get(status, status_config["进行中"])

        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
* {{margin:0;padding:0;box-sizing:border-box}}
body {{font-family:'Microsoft YaHei','PingFang SC',sans-serif;background:{config["bg"]};min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
.container {{background:rgba(255,255,255,0.98);border-radius:24px;padding:48px;box-shadow:0 25px 80px rgba(0,0,0,0.25);max-width:700px;width:100%;animation:fadeIn 0.5s ease}}
@keyframes fadeIn {{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
.header {{text-align:center;margin-bottom:40px;padding-bottom:30px;border-bottom:2px solid #f0f0f0}}
.platform-icon {{font-size:64px;margin-bottom:16px;animation:bounce 2s infinite}}
@keyframes bounce {{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-10px)}}}}
.platform-title {{font-size:36px;font-weight:800;color:#2c3e50;margin-bottom:16px;letter-spacing:-0.5px}}
.keyword-box {{background:linear-gradient(135deg,#667eea15 0%,#764ba215 100%);padding:20px 28px;border-radius:16px;margin-top:24px;border-left:5px solid {config["color"]};box-shadow:0 4px 12px rgba(0,0,0,0.05)}}
.keyword-label {{font-size:13px;color:#7f8c8d;margin-bottom:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px}}
.keyword-text {{font-size:26px;color:#2c3e50;font-weight:800;word-break:break-all}}
.progress-section {{margin:48px 0}}
.progress-header {{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}}
.progress-label {{font-size:17px;color:#7f8c8d;font-weight:700;text-transform:uppercase;letter-spacing:1px}}
.progress-numbers {{font-size:22px;color:#2c3e50;font-weight:800}}
.progress-bar-container {{width:100%;height:48px;background:#ecf0f1;border-radius:24px;overflow:hidden;position:relative;box-shadow:inset 0 2px 6px rgba(0,0,0,0.1)}}
.progress-bar {{height:100%;background:linear-gradient(90deg,{config["color"]} 0%,{config["color"]}cc 100%);width:{progress_percent}%;transition:width 0.6s cubic-bezier(0.4,0,0.2,1);display:flex;align-items:center;justify-content:flex-end;padding-right:20px;position:relative;overflow:hidden}}
.progress-bar::before {{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:linear-gradient(90deg,transparent 0%,rgba(255,255,255,0.4) 50%,transparent 100%);animation:shimmer 2.5s infinite}}
@keyframes shimmer {{0%{{transform:translateX(-100%)}}100%{{transform:translateX(100%)}}}}
.progress-percent {{color:white;font-weight:900;font-size:20px;text-shadow:0 2px 6px rgba(0,0,0,0.3);position:relative;z-index:1}}
.stats-grid {{display:grid;grid-template-columns:repeat(2,1fr);gap:28px;margin:48px 0}}
.stat-card {{background:linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%);padding:32px;border-radius:20px;text-align:center;box-shadow:0 6px 20px rgba(0,0,0,0.1);transition:all 0.3s ease}}
.stat-card:hover {{transform:translateY(-6px);box-shadow:0 12px 32px rgba(0,0,0,0.15)}}
.stat-value {{font-size:56px;font-weight:900;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:12px}}
.stat-label {{font-size:15px;color:#7f8c8d;font-weight:700;text-transform:uppercase;letter-spacing:1.5px}}
.status-section {{text-align:center;margin-top:48px}}
.status-badge {{display:inline-flex;align-items:center;gap:14px;padding:20px 48px;border-radius:32px;background:{config["color"]};color:white;font-size:22px;font-weight:800;box-shadow:0 10px 30px {config["color"]}50;transition:all 0.3s ease}}
.status-badge:hover {{transform:scale(1.08);box-shadow:0 15px 40px {config["color"]}70}}
.status-icon {{font-size:28px}}
@keyframes spin {{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}
.spinner {{display:inline-block;width:28px;height:28px;border:4px solid rgba(255,255,255,0.3);border-top-color:white;border-radius:50%;animation:spin 1s linear infinite}}
.error-box {{margin-top:40px;padding:24px 28px;background:#fff5f5;border-left:6px solid #f44336;border-radius:16px;box-shadow:0 6px 20px rgba(244,67,54,0.15)}}
.error-title {{font-size:18px;font-weight:800;color:#c62828;margin-bottom:12px}}
.error-message {{font-size:15px;color:#d32f2f;line-height:1.7}}
</style></head><body>
<div class="container">
<div class="header">
<div class="platform-icon">{platform_icon}</div>
<div class="platform-title">{platform_name} 数据采集</div>
<div class="keyword-box">
<div class="keyword-label">当前关键词</div>
<div class="keyword-text">{keyword}</div>
</div>
</div>
<div class="progress-section">
<div class="progress-header">
<div class="progress-label">采集进度</div>
<div class="progress-numbers">{current} / {total}</div>
</div>
<div class="progress-bar-container">
<div class="progress-bar">
<span class="progress-percent">{progress_percent}%</span>
</div>
</div>
</div>
<div class="stats-grid">
<div class="stat-card">
<div class="stat-value">{current}</div>
<div class="stat-label">已完成</div>
</div>
<div class="stat-card">
<div class="stat-value">{total - current}</div>
<div class="stat-label">剩余</div>
</div>
</div>
<div class="status-section">
<div class="status-badge">
{"<span class='spinner'></span>" if config["spinner"] else f"<span class='status-icon'>{config['icon']}</span>"}
<span>{status}</span>
</div>
</div>
{f'<div class="error-box"><div class="error-title">❌ 错误详情</div><div class="error-message">{error}</div></div>' if error else ""}
</div>
</body></html>"""

        self.load_html(html)

    def get_url(self) -> str:
        """获取当前URL"""
        return self.current_url

    def destroy(self):
        """销毁组件"""
        if self.html_frame:
            try:
                self.html_frame.destroy()
            except:
                pass


class TkinterWebBrowserManager:
    """tkinterweb浏览器管理器（单例模式）"""
    
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
        if TkinterWebBrowserManager._instance is not None:
            raise Exception("TkinterWebBrowserManager是单例类，请使用get_instance()获取实例")
        
        self.initialized = False
        self.parent_frame = None
    
    def initialize(self, parent_frame):
        """
        初始化tkinterweb浏览器
        
        Args:
            parent_frame: 父容器Frame
        """
        if self.initialized:
            return True
        
        try:
            self.parent_frame = parent_frame
            TkinterWebBrowserManager._browser = TkinterWebBrowser(parent_frame)
            TkinterWebBrowserManager._browser.create_widget()
            
            self.initialized = True
            print("✅ tkinterweb浏览器初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ tkinterweb浏览器初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_url(self, url: str):
        """加载URL"""
        if TkinterWebBrowserManager._browser:
            TkinterWebBrowserManager._browser.load_url(url)
    
    def load_html(self, html: str):
        """加载HTML"""
        if TkinterWebBrowserManager._browser:
            TkinterWebBrowserManager._browser.load_html(html)

    def show_crawling_progress(self, platform: str, keyword: str, current: int, total: int, status: str = "进行中", error: str = ""):
        """显示采集进度"""
        if TkinterWebBrowserManager._browser:
            TkinterWebBrowserManager._browser.show_crawling_progress(platform, keyword, current, total, status, error)

    def get_url(self) -> str:
        """获取当前URL"""
        if TkinterWebBrowserManager._browser:
            return TkinterWebBrowserManager._browser.get_url()
        return ""

    def shutdown(self):
        """关闭浏览器"""
        if TkinterWebBrowserManager._browser:
            TkinterWebBrowserManager._browser.destroy()
            TkinterWebBrowserManager._browser = None

        self.initialized = False
        print("✅ tkinterweb浏览器已关闭")


# 测试代码
if __name__ == "__main__":
    print("🧪 测试tkinterweb浏览器...")
    
    root = tk.Tk()
    root.title("tkinterweb测试")
    root.geometry("800x600")
    
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    manager = TkinterWebBrowserManager.get_instance()
    manager.initialize(frame)
    
    print("✅ 浏览器组件已创建")
    print("💡 关闭窗口即可退出测试")
    
    root.mainloop()

