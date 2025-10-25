# -*- coding: utf-8 -*-
"""
资源路径工具模块
用于解决PyInstaller打包后的资源文件路径问题
"""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径，兼容开发环境和打包后的环境
    
    Args:
        relative_path: 相对于项目根目录的路径，例如 'libs/douyin.js'
    
    Returns:
        资源文件的绝对路径
    
    Examples:
        >>> get_resource_path('libs/douyin.js')
        'C:/path/to/project/libs/douyin.js'  # 开发环境
        或
        'C:/Users/xxx/AppData/Local/Temp/_MEIxxxxxx/libs/douyin.js'  # 打包后
    """
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe，使用PyInstaller的临时目录
        base_path = sys._MEIPASS
    else:
        # 如果是开发环境，使用项目根目录
        # 获取当前文件所在目录的父目录（即项目根目录）
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


def get_libs_path(filename: str) -> str:
    """
    获取libs目录下文件的绝对路径
    
    Args:
        filename: libs目录下的文件名，例如 'douyin.js'
    
    Returns:
        文件的绝对路径
    
    Examples:
        >>> get_libs_path('douyin.js')
        'C:/path/to/project/libs/douyin.js'
    """
    return get_resource_path(f'libs/{filename}')


def get_config_path(filename: str) -> str:
    """
    获取config目录下文件的绝对路径
    
    Args:
        filename: config目录下的文件名
    
    Returns:
        文件的绝对路径
    """
    return get_resource_path(f'config/{filename}')


def get_docs_path(filename: str) -> str:
    """
    获取docs目录下文件的绝对路径
    
    Args:
        filename: docs目录下的文件名
    
    Returns:
        文件的绝对路径
    """
    return get_resource_path(f'docs/{filename}')

