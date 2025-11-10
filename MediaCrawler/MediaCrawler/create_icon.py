#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将原神PNG图片转换为ICO图标
"""

from PIL import Image
import os

def png_to_ico(png_path, ico_path):
    """将PNG图片转换为ICO图标"""
    try:
        # 打开PNG图片
        img = Image.open(png_path)

        # 转换为RGBA模式(如果不是)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 创建多种尺寸的图标
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        images = []

        for size in icon_sizes:
            # 调整大小,保持纵横比
            resized = img.copy()
            resized.thumbnail(size, Image.Resampling.LANCZOS)

            # 创建正方形背景
            background = Image.new('RGBA', size, (0, 0, 0, 0))

            # 居中粘贴
            offset = ((size[0] - resized.size[0]) // 2, (size[1] - resized.size[1]) // 2)
            background.paste(resized, offset)

            images.append(background)

        # 保存为ICO文件
        images[0].save(ico_path, format='ICO', sizes=[img.size for img in images])

        print(f"✅ 图标转换成功!")
        print(f"   源文件: {png_path}")
        print(f"   目标文件: {ico_path}")
        return True

    except Exception as e:
        print(f"❌ 图标转换失败: {e}")
        return False

if __name__ == '__main__':
    # 原神图片路径
    png_path = r"C:\Users\Yu feng\Desktop\评论抓取\软件外形\原神_爱给网_aigei_com.png"

    # 输出ICO路径
    ico_path = os.path.join(os.path.dirname(__file__), 'icon.ico')

    # 转换
    png_to_ico(png_path, ico_path)

