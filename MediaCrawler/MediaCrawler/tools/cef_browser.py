"""
CEF浏览器内嵌模块
用于在CustomTkinter GUI中嵌入Chromium浏览器
"""

import os
import sys
import platform
import threading
import time
from typing import Optional, Callable, Dict, Any
import tkinter as tk

try:
    from cefpython3 import cefpython as cef
except ImportError:
    print("❌ 错误: 未安装 cefpython3")
    print("请运行: pip install cefpython3==66.1")
    sys.exit(1)


class CEFBrowser:
    """CEF浏览器封装类"""
    
    def __init__(self, parent_frame: tk.Frame):
        """
        初始化CEF浏览器
        
        Args:
            parent_frame: Tkinter父容器
        """
        self.parent_frame = parent_frame
        self.browser = None
        self.is_initialized = False
        self.message_loop_thread = None
        self._url_change_callback = None
        self._load_complete_callback = None
        
        # CEF设置
        self.settings = {
            "debug": False,
            "log_severity": cef.LOGSEVERITY_INFO,
            "log_file": "logs/cef_debug.log",
        }
        
        # 浏览器设置
        self.browser_settings = {
            "file_access_from_file_urls_allowed": True,
            "universal_access_from_file_urls_allowed": True,
        }
        
    def initialize(self, start_url: str = "about:blank") -> bool:
        """
        初始化CEF浏览器
        
        Args:
            start_url: 初始URL
            
        Returns:
            是否初始化成功
        """
        try:
            # 检查是否已初始化
            if self.is_initialized:
                print("⚠️ CEF浏览器已经初始化")
                return True
            
            # 确保日志目录存在
            os.makedirs("logs", exist_ok=True)
            
            # 初始化CEF
            sys.excepthook = cef.ExceptHook  # 设置异常处理
            cef.Initialize(self.settings)
            
            # 获取窗口句柄
            window_handle = self.parent_frame.winfo_id()
            
            # 创建窗口信息
            window_info = cef.WindowInfo()
            window_info.SetAsChild(window_handle)
            
            # 创建浏览器
            self.browser = cef.CreateBrowserSync(
                window_info=window_info,
                settings=self.browser_settings,
                url=start_url
            )
            
            # 设置客户端处理器
            self._setup_handlers()
            
            # 标记为已初始化
            self.is_initialized = True
            
            # 启动消息循环
            self._start_message_loop()
            
            print("✅ CEF浏览器初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ CEF浏览器初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _setup_handlers(self):
        """设置浏览器事件处理器"""
        if not self.browser:
            return
        
        # 创建加载处理器
        load_handler = LoadHandler(self)
        self.browser.SetClientHandler(load_handler)
    
    def _start_message_loop(self):
        """启动CEF消息循环（在独立线程中）"""
        def message_loop():
            cef.MessageLoop()
        
        # 在主线程中运行消息循环
        # 注意：CEF的消息循环必须在主线程中运行
        # 但我们使用MessageLoopWork来避免阻塞
        pass
    
    def message_loop_work(self):
        """
        执行一次消息循环工作
        应该在GUI的主循环中定期调用
        """
        if self.is_initialized:
            cef.MessageLoopWork()
    
    def load_url(self, url: str):
        """
        加载URL
        
        Args:
            url: 要加载的URL
        """
        if self.browser:
            self.browser.LoadUrl(url)
            print(f"🌐 加载URL: {url}")
        else:
            print("❌ 浏览器未初始化")
    
    def load_html(self, html: str, base_url: str = ""):
        """
        加载HTML内容
        
        Args:
            html: HTML内容
            base_url: 基础URL
        """
        if self.browser:
            # 使用data URI加载HTML
            import base64
            html_base64 = base64.b64encode(html.encode('utf-8')).decode('utf-8')
            data_uri = f"data:text/html;base64,{html_base64}"
            self.browser.LoadUrl(data_uri)
            print(f"📄 加载HTML内容 ({len(html)} 字符)")
        else:
            print("❌ 浏览器未初始化")
    
    def execute_javascript(self, code: str):
        """
        执行JavaScript代码
        
        Args:
            code: JavaScript代码
        """
        if self.browser:
            self.browser.ExecuteJavascript(code)
            print(f"⚡ 执行JavaScript: {code[:50]}...")
        else:
            print("❌ 浏览器未初始化")
    
    def get_url(self) -> str:
        """
        获取当前URL
        
        Returns:
            当前URL
        """
        if self.browser:
            return self.browser.GetUrl()
        return ""
    
    def go_back(self):
        """后退"""
        if self.browser and self.browser.CanGoBack():
            self.browser.GoBack()
    
    def go_forward(self):
        """前进"""
        if self.browser and self.browser.CanGoForward():
            self.browser.GoForward()
    
    def reload(self):
        """刷新"""
        if self.browser:
            self.browser.Reload()
    
    def stop_load(self):
        """停止加载"""
        if self.browser:
            self.browser.StopLoad()
    
    def set_url_change_callback(self, callback: Callable[[str], None]):
        """
        设置URL变化回调
        
        Args:
            callback: 回调函数，参数为新URL
        """
        self._url_change_callback = callback
    
    def set_load_complete_callback(self, callback: Callable[[str], None]):
        """
        设置页面加载完成回调
        
        Args:
            callback: 回调函数，参数为URL
        """
        self._load_complete_callback = callback
    
    def shutdown(self):
        """关闭浏览器"""
        if self.is_initialized:
            print("🔄 正在关闭CEF浏览器...")
            if self.browser:
                self.browser.CloseBrowser(True)
                self.browser = None
            cef.Shutdown()
            self.is_initialized = False
            print("✅ CEF浏览器已关闭")
    
    def __del__(self):
        """析构函数"""
        self.shutdown()


class LoadHandler:
    """页面加载处理器"""
    
    def __init__(self, cef_browser: CEFBrowser):
        self.cef_browser = cef_browser
    
    def OnLoadingStateChange(self, browser, is_loading, **_):
        """加载状态变化"""
        if not is_loading:
            # 页面加载完成
            url = browser.GetUrl()
            if self.cef_browser._load_complete_callback:
                self.cef_browser._load_complete_callback(url)
    
    def OnLoadStart(self, browser, **_):
        """开始加载"""
        url = browser.GetUrl()
        if self.cef_browser._url_change_callback:
            self.cef_browser._url_change_callback(url)


# 全局初始化标志
_cef_initialized = False

def ensure_cef_initialized():
    """确保CEF全局初始化"""
    global _cef_initialized
    if not _cef_initialized:
        sys.excepthook = cef.ExceptHook
        _cef_initialized = True

