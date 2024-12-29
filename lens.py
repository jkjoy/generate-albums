import os
import shutil
import re
from PIL import Image
from jinja2 import Template

# 定义图片目录
photos_dir = 'photos'  # 原始图片目录
output_dir = 'output'  # 输出目录
thumb_dir = os.path.join(output_dir, 'images/thumbs')  # 缩略图目录
full_dir = os.path.join(output_dir, 'images/fulls')    # 原图目录

# 打印路径
print(f"photos_dir: {photos_dir}")
print(f"output_dir: {output_dir}")
print(f"thumb_dir: {thumb_dir}")
print(f"full_dir: {full_dir}")

# 创建输出目录、缩略图和原图目录
os.makedirs(output_dir, exist_ok=True)
os.makedirs(thumb_dir, exist_ok=True)
os.makedirs(full_dir, exist_ok=True)

# 清理文件名中的特殊字符
def clean_filename(filename):
    # 移除或替换特殊字符
    cleaned = re.sub(r'[\\/:*?"<>|,]', '_', filename)  # 替换为下划线
    return cleaned

# 获取图片文件列表（支持子目录）
images = []
try:
    for root, dirs, files in os.walk(photos_dir):
        # 查找当前目录下的 `描述.txt` 文件
        description_file = os.path.join(root, '描述.txt')
        default_description = None
        if os.path.exists(description_file):
            with open(description_file, 'r', encoding='utf-8') as f:
                default_description = f.read().strip()  # 读取 `描述.txt` 的内容

        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                original_path = os.path.join(root, filename)
                print(f"Found image: {original_path}")
                cleaned_filename = clean_filename(filename)  # 清理文件名
                thumb_path = os.path.join(thumb_dir, cleaned_filename)
                full_path = os.path.join(full_dir, cleaned_filename)

                try:
                    # 打开图片并处理
                    with Image.open(original_path) as img:
                        # 如果图片是RGBA模式，转换为RGB模式
                        if img.mode == 'RGBA':
                            img = img.convert('RGB')

                        # 保存去除 EXIF 信息后的图片
                        img.save(full_path, quality=95)  # 不传递 exif 参数，去除所有 EXIF 信息

                        # 生成缩略图
                        img.thumbnail((400, 400))  # 缩略图大小 
                        img.save(thumb_path, quality=80)  # 压缩质量

                    # 设置标题
                    if root == photos_dir:
                        title = '分享生活'  # 根目录下的图片使用默认标题
                    else:
                        title = os.path.basename(root)  # 子目录下的图片使用子目录名称作为标题

                    # 设置描述
                    description = filename  # 默认描述为文件名
                    txt_file = os.path.join(root, os.path.splitext(filename)[0] + '.txt')  # 查找同名的txt文件
                    if os.path.exists(txt_file):  # 如果存在同名的txt文件
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            description = f.read().strip()  # 读取txt文件内容作为描述
                    elif default_description is not None:  # 如果存在 `描述.txt` 文件
                        description = default_description  # 使用 `描述.txt` 的内容作为描述

                    # 添加图片信息
                    images.append({
                        'full_path': os.path.join('images/fulls', cleaned_filename).replace('\\', '/'),  # 相对于 output 目录的路径
                        'thumb_path': os.path.join('images/thumbs', cleaned_filename).replace('\\', '/'),  # 相对于 output 目录的路径
                        'title': title,  # 使用子目录名称或默认标题
                        'description': description  # 使用txt文件内容或默认描述
                    })
                except Exception as e:
                    print(f"无法处理文件 {original_path}，错误：{e}")
                    continue  # 跳过该文件，继续处理下一个文件
except Exception as e:
    print(f"遍历图片目录时出错: {e}")

# 读取HTML模板
template_path = 'templates/lens/index.html'
if not os.path.exists(template_path):
    print(f"Template file not found: {template_path}")
else:
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()

        # 使用Jinja2模板引擎
        template = Template(template_content)

        # 同步模板目录中的 assets 到 output 目录
        template_assets_dir = 'templates/lens/assets'
        output_assets_dir = os.path.join(output_dir, 'assets')

        if os.path.exists(template_assets_dir):
            shutil.rmtree(output_assets_dir, ignore_errors=True)  # 删除旧的 assets 目录
            shutil.copytree(template_assets_dir, output_assets_dir)  # 复制新的 assets 目录
            print(f"已同步 {template_assets_dir} 到 {output_assets_dir}")

        # 生成单页 HTML 内容
        html_content = template.render(images=images)
        output_file = os.path.join(output_dir, 'index.html')
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"相册页面已生成，保存为 {output_file}")
    except Exception as e:
        print(f"生成 HTML 文件时出错: {e}")