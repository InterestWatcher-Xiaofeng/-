"""
测试后端代码是否能正常运行
直接使用main.py的方式测试
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import config
from config import dy_config


async def test_douyin_search():
    """测试抖音关键词搜索"""
    print("=" * 60)
    print("🔥 开始测试抖音后端代码")
    print("=" * 60)

    # 修改配置
    print("\n📝 步骤1: 设置测试配置...")
    config.PLATFORM = "dy"
    config.KEYWORDS = "美食"
    config.CRAWLER_TYPE = "search"
    config.CRAWLER_MAX_NOTES_COUNT = 5
    config.ENABLE_GET_COMMENTS = True
    config.ENABLE_GET_SUB_COMMENTS = False
    dy_config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 10

    print(f"✅ 配置完成:")
    print(f"   平台: {config.PLATFORM}")
    print(f"   关键词: {config.KEYWORDS}")
    print(f"   视频数量: {config.CRAWLER_MAX_NOTES_COUNT}")
    print(f"   评论数量: {dy_config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES}")

    # 导入并运行main
    print("\n📝 步骤2: 启动爬虫...")
    try:
        from main import main
        await main()

        print("\n✅ 爬虫运行完成!")

        # 检查输出文件
        print("\n📝 步骤3: 检查输出文件...")
        data_dir = Path(__file__).parent / "data"
        csv_files = sorted(data_dir.glob("抖音_*_评论_*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)

        if csv_files:
            print(f"✅ 找到 {len(csv_files)} 个CSV文件:")
            for f in csv_files[:3]:  # 显示最新的3个
                size = f.stat().st_size
                print(f"   📄 {f.name} ({size} bytes)")

                # 读取并显示前几行
                if size > 0:
                    with open(f, 'r', encoding='utf-8') as file:
                        lines = file.readlines()[:3]
                        print(f"      内容预览: {len(lines)} 行")
        else:
            print("❌ 未找到CSV文件")

        print("\n" + "=" * 60)
        print("🎉 测试完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 启动后端测试...")
    asyncio.run(test_douyin_search())

