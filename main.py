#!/usr/bin/env python3
"""
Cross-Poster 多平台发布工具
支持将Markdown文章一键发布到多个内容平台
当前版本：v1.0 - 支持掘金平台
"""

import os
import sys
import json
import time
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from platforms.juejin import JuejinPublisher
from category_selector import CategorySelector

def print_banner():
    """打印程序横幅"""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║          Cross-Poster v1.0                ║
    ║       多平台内容同步发布工具                ║
    ║                                           ║
    ║    🚀 一次编写，多处发布                   ║
    ║    📝 专注创作，告别重复劳动               ║
    ║    🔧 开源免费，持续更新                   ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)

def load_config():
    """加载配置文件"""
    config_file = 'config.json'
    
    if not os.path.exists(config_file):
        print(f"❌ 错误: 找不到配置文件 '{config_file}'")
        print("请按照以下步骤操作:")
        print("1. 复制 config.example.json 为 config.json")
        print("2. 在 config.json 中填入您的平台配置信息")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证必要配置
        if 'juejin' not in config or 'cookie' not in config['juejin']:
            print("❌ 错误: 配置文件中缺少掘金Cookie")
            print("请在 config.json 的 juejin 部分添加 cookie 字段")
            return None
        
        return config
    
    except json.JSONDecodeError as e:
        print(f"❌ 错误: 配置文件JSON格式错误")
        print(f"错误详情: {e}")
        return None
    except Exception as e:
        print(f"❌ 错误: 读取配置文件失败")
        print(f"错误详情: {e}")
        return None

def find_markdown_files():
    """查找当前目录下的Markdown文件"""
    print("\n📁 搜索Markdown文件...")
    
    md_files = []
    for file in os.listdir('.'):
        if file.endswith('.md'):
            md_files.append(file)
    
    if not md_files:
        print("ℹ️  当前目录下没有找到Markdown文件 (.md)")
        print("请将您的文章保存为 .md 文件放在此目录下")
        return []
    
    print(f"✅ 找到 {len(md_files)} 个Markdown文件:")
    for i, file in enumerate(md_files, 1):
        file_size = os.path.getsize(file)
        print(f"  {i:2d}. {file} ({file_size:,} bytes)")
    
    return md_files

def select_markdown_file(files):
    """让用户选择要发布的Markdown文件"""
    if not files:
        return None
    
    if len(files) == 1:
        print(f"\n📄 自动选择唯一文件: {files[0]}")
        return files[0]
    
    print("\n" + "="*50)
    print("请选择要发布的文章")
    print("="*50)
    
    while True:
        try:
            choice = input(f"请输入文件编号 (1-{len(files)}): ").strip()
            if not choice:
                continue
                
            choice_num = int(choice)
            if 1 <= choice_num <= len(files):
                selected_file = files[choice_num-1]
                print(f"✅ 已选择: {selected_file}")
                return selected_file
            else:
                print(f"⚠️  请输入1-{len(files)}之间的数字")
                
        except ValueError:
            print("⚠️  请输入有效的数字")
        except KeyboardInterrupt:
            print("\n👋 用户取消选择")
            return None

def read_markdown_file(filepath):
    """读取Markdown文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print(f"⚠️  警告: 文件 '{filepath}' 内容为空")
            return None, None
        
        # 尝试从文件第一行提取标题
        lines = content.strip().split('\n')
        title = None
        
        # 查找第一个#开头的行作为标题
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # 如果没有找到标题，使用文件名（去掉扩展名）
        if not title:
            title = os.path.splitext(os.path.basename(filepath))[0]
        
        print(f"📖 读取文件: {filepath}")
        print(f"  标题: {title}")
        print(f"  大小: {len(content):,} 字符")
        
        return title, content
    
    except FileNotFoundError:
        print(f"❌ 错误: 文件 '{filepath}' 不存在")
        return None, None
    except Exception as e:
        print(f"❌ 错误: 读取文件失败")
        print(f"错误详情: {e}")
        return None, None

def confirm_publish(title, category_name, tags_count):
    """确认发布信息"""
    print("\n" + "="*60)
    print("📋 发布信息确认")
    print("="*60)
    print(f"  标题: {title}")
    print(f"  分类: {category_name}")
    print(f"  标签: {tags_count} 个")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    while True:
        confirm = input("\n确认发布？(y/n): ").strip().lower()
        
        if confirm in ['y', 'yes', '是', '确认']:
            return True
        elif confirm in ['n', 'no', '否', '取消']:
            print("发布已取消")
            return False
        else:
            print("⚠️  请输入 y(是) 或 n(否)")

def main():
    """主函数"""
    # 清屏并显示横幅
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    print("🔄 初始化程序...")
    
    # 1. 加载配置
    config = load_config()
    if not config:
        return
    
    # 2. 初始化掘金发布器
    try:
        cookie = config['juejin']['cookie']
        publisher = JuejinPublisher(cookie)
        
        # 测试Cookie有效性
        if not publisher.verify_login():
            print("\n❌ Cookie无效，请检查config.json中的配置")
            print("💡 获取Cookie方法:")
            print("   1. 在浏览器中登录掘金")
            print("   2. 按F12打开开发者工具")
            print("   3. 进入Network标签，刷新页面")
            print("   4. 复制第一个请求的Cookie值")
            return
        
    except KeyError:
        print("❌ 配置错误: config.json中缺少必要的掘金配置")
        return
    
    # 3. 查找并选择Markdown文件
    md_files = find_markdown_files()
    if not md_files:
        return
    
    selected_file = select_markdown_file(md_files)
    if not selected_file:
        return
    
    # 4. 读取文件内容
    title, content = read_markdown_file(selected_file)
    if not title or not content:
        return
    
    # 5. 选择分类和标签
    print("\n" + "="*60)
    print("🏷️  设置文章分类和标签")
    print("="*60)
    
    selector = CategorySelector(cookie)
    
    # 选择分类
    category_info = selector.select_category_interactive()
    if not category_info:
        return
    
    category_id = category_info['category_id']
    category_name = category_info['category_name']
    
    # 选择标签
    tag_ids = selector.select_tags_interactive(category_id)
    if not tag_ids:
        return
    
    # 6. 确认发布
    if not confirm_publish(title, category_name, len(tag_ids)):
        return
    
    # 7. 构建文章数据
    article_data = {
        'title': title,
        'content': content,
        'category_id': category_id,
        'tag_ids': tag_ids,
    }
    
    # 8. 发布文章
    print("\n" + "="*60)
    print("🚀 开始发布文章到掘金")
    print("="*60)
    
    start_time = time.time()
    
    result = publisher.publish_article(article_data)
    
    elapsed_time = time.time() - start_time
    
    # 9. 显示结果
    print("\n" + "="*60)
    print("📊 发布结果")
    print("="*60)
    
    if result.get('success'):
        print(f"✅ 发布成功！")
        print(f"   文章ID: {result.get('article_id')}")
        print(f"   文章链接: {result.get('url')}")
        print(f"   耗时: {elapsed_time:.1f}秒")
        
        # 保存发布记录
        save_publish_record(selected_file, result)
    else:
        print(f"❌ 发布失败")
        print(f"   错误: {result.get('error')}")
        print(f"   耗时: {elapsed_time:.1f}秒")
    
    print("="*60)
    print("\n感谢使用 Cross-Poster！✨")

def save_publish_record(filename, result):
    """保存发布记录"""
    record = {
        'filename': filename,
        'platform': 'juejin',
        'article_id': result.get('article_id'),
        'url': result.get('url'),
        'timestamp': datetime.now().isoformat(),
        'success': result.get('success', False),
    }
    
    # 创建记录文件
    record_file = 'publish_history.json'
    records = []
    
    # 读取现有记录
    if os.path.exists(record_file):
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        except:
            records = []
    
    # 添加新记录
    records.append(record)
    
    # 保存记录
    try:
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"📝 发布记录已保存到 {record_file}")
    except:
        print("⚠️  警告: 无法保存发布记录")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序发生未预期错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 等待用户按回车键退出
    input("\n按回车键退出...")
