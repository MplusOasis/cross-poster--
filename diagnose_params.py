# 保存为 diagnose_params.py
import requests
import json
import time

def diagnose_parameters():
    print("=== 掘金发布参数诊断 ===\n")
    
    # 1. 加载配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        cookie = config['juejin']['cookie']
        print("✅ 配置文件读取成功")
    except Exception as e:
        print(f"❌ 配置文件错误: {e}")
        return
    
    # 2. 准备测试参数
    test_params = [
        {
            "name": "最简参数测试",
            "data": {
                "category_id": "6809637767543259144",  # 后端分类
                "tag_ids": ["6809640408797167623"],    # 后端标签
                "title": f"测试文章-{int(time.time())}",
                "brief_content": "这是一个测试文章摘要。",
                "mark_content": "# 测试文章\n\n这是一个测试内容。",
                "edit_type": 10
            }
        },
        {
            "name": "完整参数测试",
            "data": {
                "category_id": "6809637767543259144",
                "tag_ids": ["6809640408797167623"],
                "link_url": "",
                "cover_image": "",
                "title": f"完整测试-{int(time.time())}",
                "brief_content": "摘要内容，不少于50字。" * 2,
                "edit_type": 10,
                "html_content": "<h1>测试</h1><p>HTML内容</p >",
                "mark_content": "# 测试\n\nMarkdown内容",
                "theme_id": "0"
            }
        }
    ]
    
    # 3. 测试发布接口
    url = 'https://api.juejin.cn/content_api/v1/article/publish'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/json',
        'Cookie': cookie,
        'Referer': 'https://juejin.cn/editor/drafts/new',
        'Origin': 'https://juejin.cn'
    }
    
    for i, test in enumerate(test_params, 1):
        print(f"\n[测试 {i}] {test['name']}")
        print("-" * 50)
        
        print("发送参数:")
        print(json.dumps(test['data'], ensure_ascii=False, indent=2))
        
        try:
            response = requests.post(url, headers=headers, json=test['data'], timeout=10)
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("响应内容:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
                if result.get('err_no') == 0:
                    print("✅ 测试成功！")
                else:
                    print(f"❌ 错误: {result.get('err_msg')}")
                    print(f"错误码: {result.get('err_no')}")
                    
                    # 分析常见错误
                    err_msg = result.get('err_msg', '').lower()
                    if 'category' in err_msg or '分类' in err_msg:
                        print("⚠️  可能是分类ID错误")
                    elif 'tag' in err_msg or '标签' in err_msg:
                        print("⚠️  可能是标签ID错误")
                    elif 'title' in err_msg or '标题' in err_msg:
                        print("⚠️  标题不符合要求")
                    elif 'brief' in err_msg or '摘要' in err_msg:
                        print("⚠️  摘要不符合要求")
                    elif 'content' in err_msg or '内容' in err_msg:
                        print("⚠️  内容不符合要求")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    diagnose_parameters()