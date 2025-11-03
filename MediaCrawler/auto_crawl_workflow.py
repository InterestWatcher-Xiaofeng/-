"""
自动化爬虫工作流 - 支持多关键词批量处理
完整流程: RPA搜索 → 获取链接 → Detail模式抓取评论

模块1: 多关键词搜索模式
- 输入多个关键词 (逗号分隔)
- 每个关键词自动搜索并收集指定数量视频链接
- 调用Detail模式批量抓取所有视频的评论
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from rpa_search_crawler import RPASearchCrawler
from config import base_config


class AutoCrawlWorkflow:
    """自动化爬虫工作流"""
    
    def __init__(self):
        self.keywords = []  # 关键词列表
        self.max_videos = None  # 每个关键词的视频数
        self.max_comments = None  # 每个视频的评论数
        self.all_video_links = []  # 所有视频链接
        
    def show_banner(self):
        """显示横幅"""
        print("\n" + "=" * 70)
        print(" " * 15 + "🚀 模块1: 多关键词搜索模式 🚀")
        print("=" * 70)
        print("\n📋 工作流程:")
        print("   第1步: RPA模式搜索多个关键词")
        print("   第2步: 自动收集所有视频链接")
        print("   第3步: Detail模式批量抓取评论")
        print("   第4步: 导出CSV数据")
        print("\n💡 特点:")
        print("   ✅ 支持多关键词 (逗号分隔)")
        print("   ✅ 每个关键词独立搜索")
        print("   ✅ 自动合并所有视频链接")
        print("   ✅ 批量抓取所有评论")
        print("\n" + "=" * 70)
    
    def get_user_input(self):
        """获取用户输入"""
        print("\n📝 请输入参数:")

        # 关键词 (支持多个,逗号分隔)
        default_keyword = base_config.KEYWORDS
        keyword_input = input(f"   关键词 (多个用逗号分隔,默认: {default_keyword}): ").strip()
        keyword_str = keyword_input if keyword_input else default_keyword

        # 解析关键词列表
        self.keywords = [k.strip() for k in keyword_str.split(',') if k.strip()]

        # 每个关键词的视频数量
        default_count = base_config.CRAWLER_MAX_NOTES_COUNT
        count_input = input(f"   每个关键词视频数 (默认: {default_count}): ").strip()
        self.max_videos = int(count_input) if count_input else default_count

        # 每个视频评论数
        default_comments = base_config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES
        comments_input = input(f"   每个视频评论数 (默认: {default_comments}): ").strip()
        self.max_comments = int(comments_input) if comments_input else default_comments

        print("\n" + "=" * 70)
        print("✅ 参数确认:")
        print(f"   🔍 关键词: {', '.join(self.keywords)} (共{len(self.keywords)}个)")
        print(f"   🎬 每个关键词视频数: {self.max_videos}")
        print(f"   💬 每个视频评论数: {self.max_comments}")
        print(f"   📊 预计总视频数: {len(self.keywords) * self.max_videos}")
        print(f"   📊 预计总评论数: {len(self.keywords) * self.max_videos * self.max_comments}")
        print("=" * 70)

        confirm = input("\n是否开始执行? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ 已取消")
            sys.exit(0)
    
    async def step1_rpa_search(self):
        """第1步: RPA搜索 - 支持多关键词"""
        print("\n" + "🔍" * 35)
        print("第1步: RPA模式搜索关键词")
        print("🔍" * 35)

        # 遍历每个关键词
        for idx, keyword in enumerate(self.keywords, 1):
            print(f"\n📌 处理关键词 {idx}/{len(self.keywords)}: {keyword}")
            print("-" * 70)

            # 创建RPA爬虫
            crawler = RPASearchCrawler(
                keyword=keyword,
                max_videos=self.max_videos
            )

            # 执行搜索
            video_links = await crawler.start()
            self.all_video_links.extend(video_links)

            print(f"✅ 关键词 '{keyword}' 完成! 收集到 {len(video_links)} 个视频链接")

            # 如果不是最后一个关键词,等待一下
            if idx < len(self.keywords):
                print("⏳ 等待3秒后处理下一个关键词...")
                await asyncio.sleep(3)

        print(f"\n✅ 第1步完成! 总共收集到 {len(self.all_video_links)} 个视频链接")
    
    def step2_update_config(self):
        """第2步: 更新配置"""
        print("\n" + "⚙️" * 35)
        print("第2步: 更新配置文件")
        print("⚙️" * 35)
        
        # 配置已在RPA爬虫中自动更新
        print("✅ 配置文件已自动更新")
    
    def step3_crawl_comments(self):
        """第3步: 抓取评论"""
        print("\n" + "💬" * 35)
        print("第3步: Detail模式抓取评论")
        print("💬" * 35)
        
        print("\n🚀 正在启动评论抓取...")
        print("   (这可能需要几分钟到几十分钟,取决于视频数量)")
        
        # 运行main.py
        cmd = [
            sys.executable,
            "main.py",
            "--platform", "dy",
            "--lt", "qrcode",
            "--type", "detail"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=Path(__file__).parent,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print("\n✅ 第3步完成! 评论抓取成功")
            else:
                print("\n⚠️ 评论抓取可能遇到问题,请查看日志")
                
        except Exception as e:
            print(f"\n❌ 评论抓取失败: {e}")
    
    def step4_show_results(self):
        """第4步: 显示结果"""
        print("\n" + "📊" * 35)
        print("第4步: 查看结果")
        print("📊" * 35)
        
        # 查找输出文件
        data_dir = Path("data/douyin/csv")
        
        if data_dir.exists():
            csv_files = list(data_dir.glob("*.csv"))
            
            if csv_files:
                print("\n✅ 数据文件已生成:")
                for csv_file in sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                    size_kb = csv_file.stat().st_size / 1024
                    mtime = datetime.fromtimestamp(csv_file.stat().st_mtime)
                    print(f"   📄 {csv_file.name}")
                    print(f"      大小: {size_kb:.1f} KB")
                    print(f"      时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("\n⚠️ 未找到CSV文件")
        else:
            print("\n⚠️ 数据目录不存在")
    
    def show_summary(self):
        """显示总结"""
        print("\n" + "=" * 70)
        print(" " * 25 + "🎉 工作流完成! 🎉")
        print("=" * 70)

        print("\n📊 执行总结:")
        print(f"   🔍 关键词: {', '.join(self.keywords)} (共{len(self.keywords)}个)")
        print(f"   🎬 视频数量: {len(self.all_video_links)}")
        print(f"   💬 评论数据: 已保存到 data/douyin/csv/")

        print("\n📁 输出文件:")
        print("   1. 视频链接: data/douyin/links/")
        print("   2. 视频信息: data/douyin/csv/detail_contents_*.csv")
        print("   3. 评论数据: data/douyin/csv/detail_comments_*.csv")

        print("\n💡 下一步:")
        print("   - 使用Excel打开CSV文件查看数据")
        print("   - 或使用Python进行数据分析")

        print("\n" + "=" * 70)
    
    async def run(self):
        """运行完整工作流"""
        try:
            # 显示横幅
            self.show_banner()
            
            # 获取用户输入
            self.get_user_input()
            
            # 第1步: RPA搜索
            await self.step1_rpa_search()
            
            # 第2步: 更新配置
            self.step2_update_config()
            
            # 第3步: 抓取评论
            self.step3_crawl_comments()
            
            # 第4步: 显示结果
            self.step4_show_results()
            
            # 显示总结
            self.show_summary()
            
        except KeyboardInterrupt:
            print("\n\n⚠️ 用户中断执行")
        except Exception as e:
            print(f"\n\n❌ 执行出错: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    workflow = AutoCrawlWorkflow()
    await workflow.run()


if __name__ == "__main__":
    asyncio.run(main())

