"""
CEF浏览器测试脚本
用于验证CEF浏览器是否能正常工作
"""

import tkinter as tk
import customtkinter as ctk
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from tools.cef_browser import CEFBrowser
    print("✅ CEF浏览器模块导入成功")
except ImportError as e:
    print(f"❌ CEF浏览器模块导入失败: {e}")
    print("请运行: pip install cefpython3==66.1")
    sys.exit(1)


class CEFTestApp:
    """CEF浏览器测试应用"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🧪 CEF浏览器测试")
        self.root.geometry("1200x800")
        
        self.cef_browser = None
        
        self.setup_ui()
        
        # 启动CEF消息循环
        self.root.after(10, self.cef_message_loop)
        
        # 延迟初始化CEF浏览器
        self.root.after(500, self.init_cef)
    
    def setup_ui(self):
        """设置UI"""
        # 顶部控制栏
        control_frame = ctk.CTkFrame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            control_frame,
            text="🧪 CEF浏览器测试",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", padx=10)
        
        # URL输入框
        self.url_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="输入URL...",
            width=400
        )
        self.url_entry.pack(side="left", padx=10)
        self.url_entry.insert(0, "https://www.baidu.com")
        
        # 加载按钮
        ctk.CTkButton(
            control_frame,
            text="🌐 加载",
            command=self.load_url
        ).pack(side="left", padx=5)
        
        # 刷新按钮
        ctk.CTkButton(
            control_frame,
            text="🔄 刷新",
            command=self.refresh
        ).pack(side="left", padx=5)
        
        # 后退按钮
        ctk.CTkButton(
            control_frame,
            text="◀ 后退",
            command=self.go_back
        ).pack(side="left", padx=5)
        
        # 前进按钮
        ctk.CTkButton(
            control_frame,
            text="▶ 前进",
            command=self.go_forward
        ).pack(side="left", padx=5)
        
        # 测试HTML按钮
        ctk.CTkButton(
            control_frame,
            text="📄 测试HTML",
            command=self.load_test_html
        ).pack(side="left", padx=5)
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="⏳ 正在初始化...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="right", padx=10)
        
        # CEF浏览器容器
        self.cef_frame = tk.Frame(self.root, bg='white')
        self.cef_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def init_cef(self):
        """初始化CEF浏览器"""
        try:
            self.status_label.configure(text="🚀 正在启动CEF浏览器...")
            
            # 创建CEF浏览器
            self.cef_browser = CEFBrowser(self.cef_frame)
            
            # 初始化
            success = self.cef_browser.initialize(start_url="about:blank")
            
            if success:
                self.status_label.configure(text="✅ CEF浏览器就绪")
                
                # 加载测试页面
                self.load_test_html()
            else:
                self.status_label.configure(text="❌ CEF浏览器初始化失败")
                
        except Exception as e:
            print(f"❌ 初始化CEF失败: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.configure(text=f"❌ 错误: {e}")
    
    def cef_message_loop(self):
        """CEF消息循环"""
        if self.cef_browser:
            try:
                self.cef_browser.message_loop_work()
            except Exception as e:
                print(f"❌ CEF消息循环错误: {e}")
        
        self.root.after(10, self.cef_message_loop)
    
    def load_url(self):
        """加载URL"""
        if self.cef_browser:
            url = self.url_entry.get()
            if url:
                self.status_label.configure(text=f"🌐 正在加载: {url}")
                self.cef_browser.load_url(url)
    
    def refresh(self):
        """刷新"""
        if self.cef_browser:
            self.cef_browser.reload()
            self.status_label.configure(text="🔄 刷新中...")
    
    def go_back(self):
        """后退"""
        if self.cef_browser:
            self.cef_browser.go_back()
    
    def go_forward(self):
        """前进"""
        if self.cef_browser:
            self.cef_browser.go_forward()
    
    def load_test_html(self):
        """加载测试HTML"""
        if self.cef_browser:
            test_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {
                        font-family: 'Microsoft YaHei', Arial, sans-serif;
                        margin: 0;
                        padding: 40px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: rgba(255, 255, 255, 0.1);
                        padding: 40px;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                    }
                    h1 {
                        font-size: 48px;
                        margin-bottom: 20px;
                        text-align: center;
                    }
                    .status {
                        font-size: 24px;
                        text-align: center;
                        margin: 20px 0;
                    }
                    .features {
                        margin-top: 40px;
                    }
                    .feature {
                        background: rgba(255, 255, 255, 0.2);
                        padding: 20px;
                        margin: 10px 0;
                        border-radius: 10px;
                    }
                    .feature h3 {
                        margin: 0 0 10px 0;
                        font-size: 20px;
                    }
                    .feature p {
                        margin: 0;
                        opacity: 0.9;
                    }
                    .test-button {
                        background: #4CAF50;
                        color: white;
                        border: none;
                        padding: 15px 30px;
                        font-size: 18px;
                        border-radius: 10px;
                        cursor: pointer;
                        margin: 10px;
                    }
                    .test-button:hover {
                        background: #45a049;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🧪 CEF浏览器测试</h1>
                    <div class="status">✅ CEF浏览器工作正常！</div>
                    
                    <div class="features">
                        <div class="feature">
                            <h3>✅ HTML渲染</h3>
                            <p>支持完整的HTML5和CSS3渲染</p>
                        </div>
                        
                        <div class="feature">
                            <h3>✅ JavaScript支持</h3>
                            <p>完整的JavaScript引擎支持</p>
                            <button class="test-button" onclick="testJS()">测试JavaScript</button>
                        </div>
                        
                        <div class="feature">
                            <h3>✅ 现代CSS</h3>
                            <p>支持渐变、阴影、动画等现代CSS特性</p>
                        </div>
                        
                        <div class="feature">
                            <h3>✅ 网络请求</h3>
                            <p>可以加载外部资源和发起网络请求</p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px;">
                        <p>在上方输入框中输入URL，点击"加载"按钮测试网页加载</p>
                        <p>推荐测试网站：</p>
                        <button class="test-button" onclick="location.href='https://www.baidu.com'">百度</button>
                        <button class="test-button" onclick="location.href='https://www.douyin.com'">抖音</button>
                        <button class="test-button" onclick="location.href='https://www.xiaohongshu.com'">小红书</button>
                    </div>
                </div>
                
                <script>
                    function testJS() {
                        alert('✅ JavaScript工作正常！\\n\\nCEF浏览器支持完整的JavaScript功能');
                    }
                    
                    console.log('✅ CEF浏览器测试页面加载成功');
                </script>
            </body>
            </html>
            """
            self.cef_browser.load_html(test_html)
            self.status_label.configure(text="📄 已加载测试HTML")
    
    def on_closing(self):
        """关闭时清理"""
        if self.cef_browser:
            print("🧹 正在关闭CEF浏览器...")
            self.cef_browser.shutdown()
        self.root.destroy()
    
    def run(self):
        """运行应用"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


if __name__ == "__main__":
    print("="*60)
    print("🧪 CEF浏览器测试程序")
    print("="*60)
    
    app = CEFTestApp()
    app.run()

