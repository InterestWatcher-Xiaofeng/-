# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


# -*- coding: utf-8 -*-
# @Author  : persist1@126.com
# @Time    : 2025/9/5 19:34
# @Desc    : 抖音存储实现类
import asyncio
import json
import os
import pathlib
from typing import Dict

from sqlalchemy import select

import config
from base.base_crawler import AbstractStore
from database.db_session import get_session
from database.models import DouyinAweme, DouyinAwemeComment, DyCreator
from tools import utils, words
from tools.async_file_writer import AsyncFileWriter
from var import crawler_type_var


class DouyinCsvStoreImplement(AbstractStore):
    def __init__(self, output_dir: str = None):
        self.file_writer = AsyncFileWriter(
            crawler_type=crawler_type_var.get(),
            platform="douyin",
            output_dir=output_dir  # 🔥 传递自定义输出目录
        )

    async def store_content(self, content_item: Dict):
        """
        Douyin content CSV storage implementation
        Args:
            content_item: note item dict

        Returns:

        """
        await self.file_writer.write_to_csv(
            item=content_item,
            item_type="contents"
        )

    async def store_comment(self, comment_item: Dict):
        """
        Douyin comment CSV storage implementation
        Args:
            comment_item: comment item dict

        Returns:

        """
        await self.file_writer.write_to_csv(
            item=comment_item,
            item_type="comments"
        )

    async def store_creator(self, creator: Dict):
        """
        Douyin creator CSV storage implementation
        Args:
            creator: creator item dict

        Returns:

        """
        await self.file_writer.write_to_csv(
            item=creator,
            item_type="creators"
        )


class DouyinDbStoreImplement(AbstractStore):
    async def store_content(self, content_item: Dict):
        """
        Douyin content DB storage implementation
        Args:
            content_item: content item dict
        """
        aweme_id = content_item.get("aweme_id")
        async with get_session() as session:
            result = await session.execute(select(DouyinAweme).where(DouyinAweme.aweme_id == aweme_id))
            aweme_detail = result.scalar_one_or_none()

            if not aweme_detail:
                content_item["add_ts"] = utils.get_current_timestamp()
                if content_item.get("title"):
                    new_content = DouyinAweme(**content_item)
                    session.add(new_content)
            else:
                for key, value in content_item.items():
                    setattr(aweme_detail, key, value)
            await session.commit()

    async def store_comment(self, comment_item: Dict):
        """
        Douyin comment DB storage implementation
        Args:
            comment_item: comment item dict
        """
        comment_id = comment_item.get("comment_id")
        async with get_session() as session:
            result = await session.execute(select(DouyinAwemeComment).where(DouyinAwemeComment.comment_id == comment_id))
            comment_detail = result.scalar_one_or_none()

            if not comment_detail:
                comment_item["add_ts"] = utils.get_current_timestamp()
                new_comment = DouyinAwemeComment(**comment_item)
                session.add(new_comment)
            else:
                for key, value in comment_item.items():
                    setattr(comment_detail, key, value)
            await session.commit()

    async def store_creator(self, creator: Dict):
        """
        Douyin creator DB storage implementation
        Args:
            creator: creator dict
        """
        user_id = creator.get("user_id")
        async with get_session() as session:
            result = await session.execute(select(DyCreator).where(DyCreator.user_id == user_id))
            user_detail = result.scalar_one_or_none()

            if not user_detail:
                creator["add_ts"] = utils.get_current_timestamp()
                new_creator = DyCreator(**creator)
                session.add(new_creator)
            else:
                for key, value in creator.items():
                    setattr(user_detail, key, value)
            await session.commit()


class DouyinJsonStoreImplement(AbstractStore):
    def __init__(self, output_dir: str = None):
        self.file_writer = AsyncFileWriter(
            crawler_type=crawler_type_var.get(),
            platform="douyin",
            output_dir=output_dir  # 🔥 传递自定义输出目录
        )

    async def store_content(self, content_item: Dict):
        """
        content JSON storage implementation
        Args:
            content_item:

        Returns:

        """
        await self.file_writer.write_single_item_to_json(
            item=content_item,
            item_type="contents"
        )

    async def store_comment(self, comment_item: Dict):
        """
        comment JSON storage implementation
        Args:
            comment_item:

        Returns:

        """
        await self.file_writer.write_single_item_to_json(
            item=comment_item,
            item_type="comments"
        )

    async def store_creator(self, creator: Dict):
        """
        creator JSON storage implementation
        Args:
            creator:

        Returns:

        """
        await self.file_writer.write_single_item_to_json(
            item=creator,
            item_type="creators"
        )



class DouyinSqliteStoreImplement(DouyinDbStoreImplement):
    pass