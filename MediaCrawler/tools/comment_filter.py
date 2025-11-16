# 评论筛选工具
# 用于从采集的评论中筛选出需要回复的评论

import re
from typing import List, Dict

class CommentFilter:
    """评论筛选器"""

    def __init__(self):
        # 定义需要回复的关键词
        self.keywords = [
            # 询问价格
            "多少钱", "价格", "多钱", "怎么卖",

            # 询问购买
            "哪里买", "在哪买", "怎么买", "链接", "购买",

            # 询问详情
            "怎么样", "好用吗", "推荐吗", "值得吗",

            # 提问
            "？", "?", "吗", "呢",

            # 求联系
            "微信", "联系", "私信",
        ]

        # 排除的关键词（垃圾评论）
        self.exclude_keywords = [
            "互粉", "关注", "刷", "广告",
        ]

    def filter_comments(self, comments: List[Dict], mode="keyword") -> List[Dict]:
        """
        筛选评论

        Args:
            comments: 评论列表
            mode: 筛选模式
                - "keyword": 关键词匹配
                - "question": 只要问题（包含？）
                - "high_like": 高赞评论（点赞数>10）
                - "custom": 自定义规则

        Returns:
            需要回复的评论列表
        """
        result = []

        for comment in comments:
            content = comment.get("content", "")
            like_count = int(comment.get("like_count", 0))

            # 排除垃圾评论
            if self._is_spam(content):
                continue

            # 根据模式筛选
            if mode == "keyword":
                if self._contains_keywords(content):
                    result.append(comment)

            elif mode == "question":
                if "？" in content or "?" in content:
                    result.append(comment)

            elif mode == "high_like":
                if like_count > 10:
                    result.append(comment)

            elif mode == "custom":
                # 自定义规则：包含关键词 或 是问题 或 高赞
                if (self._contains_keywords(content) or
                    "？" in content or "?" in content or
                    like_count > 10):
                    result.append(comment)

        return result

    def _contains_keywords(self, content: str) -> bool:
        """检查是否包含关键词"""
        for keyword in self.keywords:
            if keyword in content:
                return True
        return False

    def _is_spam(self, content: str) -> bool:
        """检查是否是垃圾评论"""
        for keyword in self.exclude_keywords:
            if keyword in content:
                return True
        return False

    def add_keyword(self, keyword: str):
        """添加自定义关键词"""
        if keyword not in self.keywords:
            self.keywords.append(keyword)

    def add_exclude_keyword(self, keyword: str):
        """添加排除关键词"""
        if keyword not in self.exclude_keywords:
            self.exclude_keywords.append(keyword)


# 使用示例
if __name__ == "__main__":
    # 模拟评论数据
    comments = [
        {"content": "这个多少钱？", "like_count": "5", "comment_id": "123"},
        {"content": "真好看", "like_count": "2", "comment_id": "124"},
        {"content": "哪里可以买到？", "like_count": "8", "comment_id": "125"},
        {"content": "互粉走一波", "like_count": "0", "comment_id": "126"},
        {"content": "这个好用吗？", "like_count": "15", "comment_id": "127"},
    ]

    # 创建筛选器
    filter = CommentFilter()

    # 筛选评论
    filtered = filter.filter_comments(comments, mode="custom")

    print(f"原始评论数: {len(comments)}")
    print(f"需要回复的评论数: {len(filtered)}")
    print("\n需要回复的评论:")
    for c in filtered:
        print(f"  - {c['content']} (赞: {c['like_count']})")
