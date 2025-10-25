import asyncio
import csv
import json
import os
import pathlib
from typing import Dict, List, Optional
import aiofiles
from tools.utils import utils

class AsyncFileWriter:
    def __init__(self, platform: str, crawler_type: str, output_dir: Optional[str] = None):
        self.lock = asyncio.Lock()
        self.platform = platform
        self.crawler_type = crawler_type
        self.output_dir = output_dir  # 🔥 新增：自定义输出目录
        self.file_paths = {}  # 🔥 新增：记录生成的文件路径

        # 🔥 定义CSV列顺序
        self.column_orders = {
            "comments": [
                # 前三列：标题、链接、评论内容
                "video_title",
                "video_url",
                "content",
                # 评论基本信息
                "comment_id",
                "create_time",
                "ip_location",
                "like_count",
                "sub_comment_count",
                "parent_comment_id",
                # 用户信息
                "nickname",
                "user_id",
                "sec_uid",
                "short_user_id",
                "user_unique_id",
                "user_signature",
                "avatar",
                # 视频信息
                "aweme_id",
                "video_author",
                "video_liked_count",
                "video_comment_count",
                # 其他
                "pictures",
                "last_modify_ts",
            ],
            "contents": [
                # 视频内容的列顺序（保持原样）
                "aweme_id",
                "title",
                "desc",
                "create_time",
                "user_id",
                "nickname",
                "avatar",
                "liked_count",
                "comment_count",
                "share_count",
                "collected_count",
                "aweme_type",
                "aweme_url",
                "video_url",
                "video_duration",
                "music_title",
                "music_author",
                "ip_location",
                "last_modify_ts",
            ],
            "creators": [
                # 创作者的列顺序（保持原样）
                "user_id",
                "nickname",
                "gender",
                "avatar",
                "desc",
                "ip_location",
                "follows",
                "fans",
                "interaction",
                "videos_count",
                "last_modify_ts",
            ]
        }

    def _get_file_path(self, file_type: str, item_type: str) -> str:
        # 🔥 如果已经生成过该类型的文件路径，直接返回（确保同一次采集使用同一个文件）
        cache_key = f"{file_type}_{item_type}"
        if cache_key in self.file_paths:
            return self.file_paths[cache_key]

        # 🔥 如果设置了自定义输出目录，使用自定义目录
        if self.output_dir:
            base_path = self.output_dir
        else:
            base_path = f"data/{self.platform}/{file_type}"

        pathlib.Path(base_path).mkdir(parents=True, exist_ok=True)

        # 🔥 生成带时间戳的唯一文件名（每次采集都创建新文件）
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_name = f"{self.crawler_type}_{item_type}_{timestamp}.{file_type}"
        file_path = f"{base_path}/{file_name}"

        # 🔥 记录文件路径（使用cache_key作为键）
        self.file_paths[cache_key] = file_path

        return file_path

    def get_file_paths(self) -> Dict[str, str]:
        """获取所有生成的文件路径"""
        return self.file_paths.copy()

    def _get_ordered_fieldnames(self, item: Dict, item_type: str) -> List[str]:
        """
        获取有序的字段名列表

        Args:
            item: 数据项字典
            item_type: 数据类型（comments/contents/creators）

        Returns:
            有序的字段名列表
        """
        # 获取预定义的列顺序
        predefined_order = self.column_orders.get(item_type, [])

        # 获取实际数据中的所有键
        actual_keys = list(item.keys())

        # 按照预定义顺序排列存在的字段
        ordered_fields = [field for field in predefined_order if field in actual_keys]

        # 添加预定义顺序中没有的字段（放在最后）
        remaining_fields = [field for field in actual_keys if field not in predefined_order]

        return ordered_fields + remaining_fields

    async def write_to_csv(self, item: Dict, item_type: str):
        file_path = self._get_file_path('csv', item_type)
        async with self.lock:
            file_exists = os.path.exists(file_path)

            # 🔥 使用有序的字段名
            fieldnames = self._get_ordered_fieldnames(item, item_type)

            async with aiofiles.open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists or await f.tell() == 0:
                    await writer.writeheader()
                await writer.writerow(item)

    async def write_single_item_to_json(self, item: Dict, item_type: str):
        file_path = self._get_file_path('json', item_type)
        async with self.lock:
            existing_data = []
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        content = await f.read()
                        if content:
                            existing_data = json.loads(content)
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                    except json.JSONDecodeError:
                        existing_data = []
            
            existing_data.append(item)

            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(existing_data, ensure_ascii=False, indent=4))