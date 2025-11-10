#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI配置管理模块
负责GUI界面和MediaCrawler核心配置之间的同步和管理
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class PlatformConfig:
    """平台配置"""
    platform: str = "xhs"
    login_type: str = "qrcode"
    crawler_type: str = "search"
    keywords: str = ""
    detail_url: str = ""
    creator_url: str = ""

@dataclass
class CrawlerSettings:
    """爬虫设置"""
    max_notes_count: int = 20
    max_comments_count: int = 50
    start_page: int = 1
    enable_comments: bool = True
    enable_sub_comments: bool = False
    enable_wordcloud: bool = True
    enable_media: bool = False
    crawler_sleep_sec: int = 2
    max_concurrency: int = 1
    headless: bool = False

@dataclass
class OutputSettings:
    """输出设置"""
    save_format: str = "json"
    output_dir: str = "data"
    auto_open: bool = True
    generate_report: bool = True
    custom_filename: str = ""

@dataclass
class GUIConfig:
    """GUI完整配置"""
    platform: PlatformConfig
    crawler: CrawlerSettings
    output: OutputSettings
    last_updated: str = ""

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "gui_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> GUIConfig:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return GUIConfig(
                    platform=PlatformConfig(**data.get('platform', {})),
                    crawler=CrawlerSettings(**data.get('crawler', {})),
                    output=OutputSettings(**data.get('output', {})),
                    last_updated=data.get('last_updated', '')
                )
            except Exception as e:
                print(f"配置加载失败: {e}，使用默认配置")
        
        # 返回默认配置
        return GUIConfig(
            platform=PlatformConfig(),
            crawler=CrawlerSettings(),
            output=OutputSettings(),
            last_updated=datetime.now().isoformat()
        )
    
    def save_config(self):
        """保存配置"""
        try:
            self.config.last_updated = datetime.now().isoformat()
            
            config_data = {
                'platform': asdict(self.config.platform),
                'crawler': asdict(self.config.crawler),
                'output': asdict(self.config.output),
                'last_updated': self.config.last_updated
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"配置保存失败: {e}")
            return False
    
    def update_platform_config(self, **kwargs):
        """更新平台配置"""
        for key, value in kwargs.items():
            if hasattr(self.config.platform, key):
                setattr(self.config.platform, key, value)
    
    def update_crawler_settings(self, **kwargs):
        """更新爬虫设置"""
        for key, value in kwargs.items():
            if hasattr(self.config.crawler, key):
                setattr(self.config.crawler, key, value)
    
    def update_output_settings(self, **kwargs):
        """更新输出设置"""
        for key, value in kwargs.items():
            if hasattr(self.config.output, key):
                setattr(self.config.output, key, value)
    
    def apply_to_mediacrawler(self):
        """将GUI配置应用到MediaCrawler"""
        try:
            import config as mc_config
            
            # 平台配置
            mc_config.PLATFORM = self.config.platform.platform
            mc_config.LOGIN_TYPE = self.config.platform.login_type
            mc_config.CRAWLER_TYPE = self.config.platform.crawler_type
            mc_config.KEYWORDS = self.config.platform.keywords
            
            # 爬虫设置
            mc_config.CRAWLER_MAX_NOTES_COUNT = self.config.crawler.max_notes_count
            mc_config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = self.config.crawler.max_comments_count
            mc_config.START_PAGE = self.config.crawler.start_page
            mc_config.ENABLE_GET_COMMENTS = self.config.crawler.enable_comments
            mc_config.ENABLE_GET_SUB_COMMENTS = self.config.crawler.enable_sub_comments
            mc_config.ENABLE_GET_WORDCLOUD = self.config.crawler.enable_wordcloud
            mc_config.ENABLE_GET_MEIDAS = self.config.crawler.enable_media
            mc_config.CRAWLER_MAX_SLEEP_SEC = self.config.crawler.crawler_sleep_sec
            mc_config.MAX_CONCURRENCY_NUM = self.config.crawler.max_concurrency
            mc_config.HEADLESS = self.config.crawler.headless
            
            # 输出设置
            mc_config.SAVE_DATA_OPTION = self.config.output.save_format
            
            return True
        except Exception as e:
            print(f"配置应用失败: {e}")
            return False
    
    def get_platform_specific_config(self, platform: str) -> Dict[str, Any]:
        """获取平台特定配置"""
        platform_configs = {
            "xhs": {
                "sort_type": "popularity_descending",
                "specified_notes": [],
                "creator_ids": []
            },
            "dy": {
                "search_sort_type": 1,  # 按点赞数排序
                "publish_time_type": 0,
                "specified_ids": [],
                "creator_ids": []
            },
            "ks": {
                "specified_ids": [],
                "creator_ids": []
            },
            "bili": {
                "search_mode": "normal",
                "qn": 80,
                "creator_mode": True,
                "specified_ids": [],
                "creator_ids": []
            },
            "wb": {
                "specified_ids": [],
                "creator_ids": []
            },
            "tieba": {
                "specified_tieba_names": [],
                "specified_note_ids": []
            },
            "zhihu": {
                "specified_ids": [],
                "creator_ids": []
            }
        }
        
        return platform_configs.get(platform, {})
    
    def validate_config(self) -> Dict[str, list]:
        """验证配置"""
        errors = {
            "platform": [],
            "crawler": [],
            "output": []
        }
        
        # 验证平台配置
        if not self.config.platform.platform:
            errors["platform"].append("未选择平台")
        
        if self.config.platform.crawler_type == "search" and not self.config.platform.keywords:
            errors["platform"].append("搜索模式下必须输入关键词")
        
        if self.config.platform.crawler_type == "detail" and not self.config.platform.detail_url:
            errors["platform"].append("详情模式下必须输入内容链接或ID")
        
        if self.config.platform.crawler_type == "creator" and not self.config.platform.creator_url:
            errors["platform"].append("创作者模式下必须输入创作者链接或ID")
        
        # 验证爬虫设置
        if self.config.crawler.max_notes_count <= 0:
            errors["crawler"].append("最大内容数量必须大于0")
        
        if self.config.crawler.max_comments_count <= 0:
            errors["crawler"].append("最大评论数量必须大于0")
        
        if self.config.crawler.crawler_sleep_sec < 0:
            errors["crawler"].append("采集间隔不能为负数")
        
        if self.config.crawler.max_concurrency <= 0:
            errors["crawler"].append("并发数量必须大于0")
        
        # 验证输出设置
        if not self.config.output.output_dir:
            errors["output"].append("必须指定输出目录")
        
        # 移除空的错误列表
        return {k: v for k, v in errors.items() if v}
    
    def get_config_summary(self) -> str:
        """获取配置摘要"""
        platform_name = {
            "xhs": "小红书",
            "dy": "抖音", 
            "ks": "快手",
            "bili": "B站",
            "wb": "微博",
            "tieba": "贴吧",
            "zhihu": "知乎"
        }.get(self.config.platform.platform, self.config.platform.platform)
        
        mode_name = {
            "search": "关键词搜索",
            "detail": "指定内容",
            "creator": "创作者主页"
        }.get(self.config.platform.crawler_type, self.config.platform.crawler_type)
        
        format_name = {
            "csv": "CSV文件",
            "json": "JSON文件",
            "sqlite": "SQLite数据库",
            "db": "MySQL数据库"
        }.get(self.config.output.save_format, self.config.output.save_format)
        
        summary = f"""配置摘要:
平台: {platform_name}
模式: {mode_name}
关键词: {self.config.platform.keywords or '未设置'}
最大内容数: {self.config.crawler.max_notes_count}
最大评论数: {self.config.crawler.max_comments_count}
输出格式: {format_name}
输出目录: {self.config.output.output_dir}
"""
        return summary

class TaskHistory:
    """任务历史管理"""
    
    def __init__(self, history_file: str = "task_history.json"):
        self.history_file = Path(history_file)
        self.history = self.load_history()
    
    def load_history(self) -> list:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
    
    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def add_task(self, task_info: Dict[str, Any]):
        """添加任务记录"""
        task_record = {
            "timestamp": datetime.now().isoformat(),
            "platform": task_info.get("platform", ""),
            "mode": task_info.get("mode", ""),
            "keywords": task_info.get("keywords", ""),
            "status": task_info.get("status", "completed"),
            "result_count": task_info.get("result_count", 0),
            "output_file": task_info.get("output_file", ""),
            "duration": task_info.get("duration", 0)
        }
        
        self.history.insert(0, task_record)  # 最新的在前面
        
        # 保留最近100条记录
        if len(self.history) > 100:
            self.history = self.history[:100]
        
        self.save_history()
    
    def get_recent_tasks(self, limit: int = 10) -> list:
        """获取最近的任务"""
        return self.history[:limit]
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self.save_history()

# 全局配置管理器实例
config_manager = ConfigManager()
task_history = TaskHistory()
