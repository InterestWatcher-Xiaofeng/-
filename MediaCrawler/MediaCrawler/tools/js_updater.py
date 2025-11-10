# -*- coding: utf-8 -*-
"""
动态JS更新模块 - 避免签名算法失效
"""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Optional

import httpx
from tools import utils


class JSUpdater:
    """JS文件动态更新器"""
    
    def __init__(self, platform: str = "douyin"):
        self.platform = platform
        self.config_file = Path("config/js_version.json")
        self.js_dir = Path("libs")
        
        # 远程更新服务器（可以是GitHub Raw或自己的服务器）
        self.update_server = "https://raw.githubusercontent.com/your-repo/MediaCrawler/main/libs"
        
    async def check_update(self) -> bool:
        """检查是否有更新"""
        try:
            # 获取远程版本信息
            remote_version = await self._get_remote_version()
            local_version = self._get_local_version()
            
            utils.logger.info(f"[JSUpdater] 本地版本: {local_version}, 远程版本: {remote_version}")
            
            if remote_version > local_version:
                utils.logger.info(f"[JSUpdater] 发现新版本: {remote_version}")
                return True
            
            return False
        except Exception as e:
            utils.logger.warning(f"[JSUpdater] 检查更新失败: {e}")
            return False
    
    async def update(self) -> bool:
        """执行更新"""
        try:
            utils.logger.info(f"[JSUpdater] 开始更新 {self.platform}.js ...")
            
            # 下载新的JS文件
            js_content = await self._download_js()
            
            # 验证文件完整性
            if not self._validate_js(js_content):
                utils.logger.error("[JSUpdater] JS文件验证失败")
                return False
            
            # 备份旧文件
            self._backup_old_js()
            
            # 保存新文件
            js_file = self.js_dir / f"{self.platform}.js"
            js_file.write_text(js_content, encoding='utf-8')
            
            # 更新版本信息
            self._update_local_version()
            
            utils.logger.info("[JSUpdater] ✅ 更新成功")
            return True
            
        except Exception as e:
            utils.logger.error(f"[JSUpdater] 更新失败: {e}")
            # 恢复备份
            self._restore_backup()
            return False
    
    async def _get_remote_version(self) -> str:
        """获取远程版本号"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.update_server}/version.json")
            version_info = resp.json()
            return version_info.get(self.platform, {}).get('version', '0.0.0')
    
    def _get_local_version(self) -> str:
        """获取本地版本号"""
        if not self.config_file.exists():
            return "0.0.0"
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get(self.platform, {}).get('version', '0.0.0')
    
    async def _download_js(self) -> str:
        """下载JS文件"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{self.update_server}/{self.platform}.js")
            return resp.text
    
    def _validate_js(self, js_content: str) -> bool:
        """验证JS文件"""
        # 简单验证：检查是否包含关键函数
        if self.platform == "douyin":
            return "sign_datail" in js_content and "sign_reply" in js_content
        return len(js_content) > 100
    
    def _backup_old_js(self):
        """备份旧文件"""
        js_file = self.js_dir / f"{self.platform}.js"
        if js_file.exists():
            backup_file = self.js_dir / f"{self.platform}.js.bak"
            backup_file.write_bytes(js_file.read_bytes())
    
    def _restore_backup(self):
        """恢复备份"""
        backup_file = self.js_dir / f"{self.platform}.js.bak"
        if backup_file.exists():
            js_file = self.js_dir / f"{self.platform}.js"
            js_file.write_bytes(backup_file.read_bytes())
    
    def _update_local_version(self):
        """更新本地版本信息"""
        # 这里简化处理，实际应该从远程获取
        pass


async def auto_update_js(platform: str = "douyin") -> bool:
    """自动更新JS文件"""
    updater = JSUpdater(platform)
    
    if await updater.check_update():
        return await updater.update()
    
    return False


if __name__ == "__main__":
    # 测试
    asyncio.run(auto_update_js("douyin"))

