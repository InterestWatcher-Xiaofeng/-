"""
测试小红书多链接评论采集功能
使用后端代码直接测试
"""
import asyncio
import sys
from pathlib import Path
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import config
from config import xhs_config


async def test_xhs_detail():
    """测试小红书指定链接模式"""
    print("=" * 80)
    print("🔥 开始测试小红书多链接评论采集功能")
    print("=" * 80)

    # 修改配置
    print("\n📝 步骤1: 设置测试配置...")
    config.PLATFORM = "xhs"
    config.CRAWLER_TYPE = "detail"  # 指定链接模式
    config.CRAWLER_MAX_NOTES_COUNT = 2  # 采集2个笔记
    config.ENABLE_GET_COMMENTS = True  # 开启评论采集
    config.ENABLE_GET_SUB_COMMENTS = False  # 不采集二级评论
    config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 20  # 每个笔记采集20条评论
    config.SAVE_DATA_OPTION = "json"  # 保存为JSON格式
    config.HEADLESS = False  # 显示浏览器
    
    # 设置小红书链接
    xhs_config.XHS_SPECIFIED_NOTE_URL_LIST = [
        "https://www.xiaohongshu.com/explore/68e5cfe700000000070155f8?xsec_token=ABvtnJKr4wuvcowlUzmI6ABKIL5elLWjhAnZCICqxCm0g=&xsec_source=pc_feed",
        "https://www.xiaohongshu.com/explore/69041dd7000000000401446a?xsec_token=ABLpYaPvP0GLX77PLAH33eXcjZm9ekZgd1Ba4rXvqOvWc=&xsec_source=pc_feed"
    ]

    print(f"✅ 配置完成:")
    print(f"   平台: {config.PLATFORM}")
    print(f"   采集模式: {config.CRAWLER_TYPE}")
    print(f"   笔记数量: {config.CRAWLER_MAX_NOTES_COUNT}")
    print(f"   评论数量: {config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES}")
    print(f"   保存格式: {config.SAVE_DATA_OPTION}")
    print(f"\n   链接列表:")
    for i, url in enumerate(xhs_config.XHS_SPECIFIED_NOTE_URL_LIST, 1):
        note_id = url.split('/explore/')[1].split('?')[0]
        print(f"   {i}. {note_id}")

    # 导入并运行main
    print("\n📝 步骤2: 启动爬虫...")
    print("⚠️  注意: 请确保已经登录小红书!")
    print("⚠️  如果未登录,程序会打开浏览器让你扫码登录")
    print("-" * 80)
    
    try:
        from main import main
        await main()

        print("\n" + "=" * 80)
        print("✅ 爬虫运行完成!")
        print("=" * 80)

        # 检查输出文件
        print("\n📝 步骤3: 检查输出文件...")
        data_dir = Path(__file__).parent / "data" / "xhs"
        
        # 查找JSON文件
        json_files = list(data_dir.glob("*.json"))
        
        if json_files:
            # 按修改时间排序,获取最新的文件
            json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            print(f"✅ 找到 {len(json_files)} 个JSON文件:")
            
            for i, f in enumerate(json_files[:5], 1):  # 显示最新的5个
                size = f.stat().st_size
                print(f"\n   📄 文件{i}: {f.name}")
                print(f"      大小: {size} bytes ({size/1024:.2f} KB)")
                
                # 读取并分析JSON内容
                if size > 0:
                    try:
                        with open(f, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            
                            if isinstance(data, list):
                                print(f"      数据条数: {len(data)}")
                                
                                # 显示第一条数据的结构
                                if len(data) > 0:
                                    first_item = data[0]
                                    print(f"      数据字段: {', '.join(first_item.keys())}")
                                    
                                    # 如果是评论数据,显示详细信息
                                    if 'content' in first_item or 'note_id' in first_item:
                                        print(f"\n      📊 数据预览:")
                                        for j, item in enumerate(data[:3], 1):
                                            if 'content' in item:
                                                content = item.get('content', '')[:50]
                                                nickname = item.get('nickname', '未知')
                                                print(f"         {j}. {nickname}: {content}...")
                                            elif 'title' in item:
                                                title = item.get('title', '')[:50]
                                                print(f"         {j}. 笔记: {title}...")
                            else:
                                print(f"      数据类型: {type(data)}")
                                
                    except json.JSONDecodeError:
                        print(f"      ⚠️  JSON解析失败")
                    except Exception as e:
                        print(f"      ⚠️  读取失败: {e}")
        else:
            print("❌ 未找到JSON文件")
            print(f"   数据目录: {data_dir}")
            print(f"   目录是否存在: {data_dir.exists()}")
            
            if data_dir.exists():
                all_files = list(data_dir.glob("*"))
                if all_files:
                    print(f"   目录中的文件:")
                    for f in all_files:
                        print(f"      - {f.name}")

        print("\n" + "=" * 80)
        print("🎉 测试完成!")
        print("=" * 80)
        
        # 总结
        print("\n📊 测试总结:")
        print(f"   ✅ 配置正确")
        print(f"   ✅ 爬虫运行成功")
        if json_files:
            print(f"   ✅ 数据已保存 ({len(json_files)} 个文件)")
        else:
            print(f"   ⚠️  未找到数据文件")

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ 测试失败: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        
        print("\n💡 可能的原因:")
        print("   1. 未登录小红书")
        print("   2. 链接中的xsec_token已过期")
        print("   3. 网络连接问题")
        print("   4. 小红书反爬限制")


if __name__ == "__main__":
    print("🚀 启动小红书多链接测试...")
    print("⏰ 预计时间: 2-5分钟")
    print()
    asyncio.run(test_xhs_detail())

