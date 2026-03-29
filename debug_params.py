import requests
import json
import time
import hashlib

def debug_full_flow():
    print("="*60)
    print("掘金发布全流程调试")
    print("="*60)
    
    # 1. 加载您最新抓取的配置
    print("\n[1/4] 加载配置信息...")
    # 请将您最新从浏览器抓取的 headers, cookies, params 粘贴到下面的变量中
    YOUR_HEADERS = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://juejin.cn',
        'priority': 'u=1, i',
        'referer': 'https://juejin.cn/editor/drafts/new', # 确保是编辑器页面
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'x-secsdk-csrf-token': '000100000001xxxxxxxxxxxx', # 请替换为真实token
    }
    
    YOUR_COOKIES = {
        'sessionid': 'xxxxxxxxxxxxxxxxxxxxxxxx',
        'sid_guard': 'xxxxxxxxxxxxxxxxxxxxxxxx',
        'passport_auth_status': 'xxxxxxxxxxxxxxxxxxxxxxxx',
        'n_mh': 'xxxxxxxxxxxxxxxxxxxxxxxx',
        # ... 请粘贴完整的cookies
    }
    
    YOUR_PARAMS = {
        'aid': '2608',
        'uuid': '7622647391912773170', # 请确保这是您的uuid
    }
    
    print("  配置加载完成。")
    print(f"  Cookies键数量: {len(YOUR_COOKIES)}")
    print(f"  Headers键数量: {len(YOUR_HEADERS)}")
    
    # 2. 测试Cookie有效性（关键！）
    print("\n[2/4] 测试Cookie与登录状态...")
    test_url = "https://api.juejin.cn/user_api/v1/user/get"
    try:
        resp = requests.get(test_url, headers=YOUR_HEADERS, cookies=YOUR_COOKIES)
        print(f"  状态码: {resp.status_code}")
        if resp.status_code == 200:
            user_data = resp.json()
            print(f"  接口返回: {json.dumps(user_data, ensure_ascii=False)}")
            if user_data.get('err_no') == 0:
                print(f"  ✅ Cookie有效！用户名: {user_data['data'].get('user_name')}")
            else:
                print(f"  ❌ Cookie已失效或权限不足: {user_data.get('err_msg')}")
                print("  【行动项】请重新在无痕窗口中登录掘金，并抓取最新的Cookie和x-secsdk-csrf-token。")
                return
        else:
            print(f"  ❌ 用户信息请求失败，状态码: {resp.status_code}")
    except Exception as e:
        print(f"  ❌ 测试请求异常: {e}")
        return
    
    # 3. 创建草稿
    print("\n[3/4] 尝试创建草稿...")
    create_url = "https://api.juejin.cn/content_api/v1/article_draft/create"
    # 使用最简单的测试数据
    test_title = f"调试测试文章{int(time.time())}"
    test_content = "# 这是一个调试用的测试文章\n\n本文由自动化工具发布，用于测试接口连通性。\n\n" + "测试正文内容。" * 20
    test_brief = test_content[:100]
    
    draft_data = {
        "title": test_title,
        "mark_content": test_content,
        "brief_content": test_brief,
        "category_id": "6809637767543259144", # 后端分类
        "tag_ids": ["6809640408797167623"],   # 后端标签
        "edit_type": 10,
        "link_url": "",
        "cover_image": "",
    }
    
    print(f"  草稿标题: {test_title}")
    print(f"  内容长度: {len(test_content)} 字符")
    print("  发送创建草稿请求...")
    
    try:
        create_resp = requests.post(create_url, headers=YOUR_HEADERS, cookies=YOUR_COOKIES, json=draft_data)
        print(f"  状态码: {create_resp.status_code}")
        print(f"  响应头: {dict(create_resp.headers)}")
        create_result = create_resp.json()
        print(f"  响应体: {json.dumps(create_result, ensure_ascii=False, indent=2)}")
        
        if create_result.get('err_no') == 0:
            draft_id = create_result['data']['article_id']
            print(f"  ✅ 草稿创建成功！Draft ID: {draft_id}")
            
            # 保存草稿ID和可能的字数信息（关键！）
            # 注意：响应中可能有encrypted_word_count等信息，如果存在请记录
            draft_info = create_result['data']
            print(f"  草稿详情: {json.dumps(draft_info, ensure_ascii=False)}")
            
        else:
            print(f"  ❌ 草稿创建失败: {create_result.get('err_msg')}")
            print("  【可能原因】分类/标签ID失效、标题/内容格式不符、Cookie权限不足。")
            return
        
    except Exception as e:
        print(f"  ❌ 创建草稿请求异常: {e}")
        return
    
    # 4. 发布草稿
    print("\n[4/4] 尝试发布草稿...")
    if 'draft_id' not in locals():
        print("  缺少draft_id，无法进行发布测试。")
        return
        
    publish_url = "https://api.juejin.cn/content_api/v1/article/publish"
    
    # 构建发布数据
    # 注意：encrypted_word_count 和 origin_word_count 是难点
    # 方案A：尝试从创建草稿的响应中获取
    # 方案B：尝试不传或传0
    # 方案C：根据内容长度计算（需研究算法，这里先尝试方案A和B）
    
    publish_data = {
        'draft_id': draft_id,
        'sync_to_org': False,
        'column_ids': [],
        'theme_ids': [],
        # 以下是关键字段，需要确定如何获取
        'encrypted_word_count': 0,  # 先尝试0
        'origin_word_count': len(test_content), # 先传实际长度
    }
    
    # 如果您在创建草稿的响应中看到了encrypted_word_count，请取消下面这行注释
    # if 'encrypted_word_count' in draft_info:
    #     publish_data['encrypted_word_count'] = draft_info['encrypted_word_count']
    
    print(f"  发布草稿ID: {draft_id}")
    print(f"  发布请求体: {json.dumps(publish_data, ensure_ascii=False)}")
    
    # 注意：发布接口可能需要额外的params，使用您抓取的YOUR_PARAMS
    try:
        publish_resp = requests.post(
            publish_url,
            params=YOUR_PARAMS,  # 您抓取的aid, uuid等参数
            headers=YOUR_HEADERS,
            cookies=YOUR_COOKIES,
            json=publish_data,
        )
        
        print(f"  状态码: {publish_resp.status_code}")
        print(f"  响应体: {publish_resp.text}")
        
        if publish_resp.status_code == 200:
            publish_result = publish_resp.json()
            print(f"  解析后的响应: {json.dumps(publish_result, ensure_ascii=False, indent=2)}")
            
            if publish_result.get('err_no') == 0:
                article_id = publish_result.get('data', {}).get('article_id')
                print(f"  🎉 发布成功！文章ID: {article_id}")
                print(f"  文章链接: https://juejin.cn/post/{article_id}")
            else:
                err_msg = publish_result.get('err_msg')
                print(f"  ❌ 发布失败: {err_msg}")
                
                # 根据错误信息给出建议
                if "encrypted_word_count" in err_msg or "字数" in err_msg:
                    print("  【问题分析】encrypted_word_count 字段校验失败。")
                    print("  【解决方案】需要从创建草稿的响应中获取正确的值。")
                elif "draft_id" in err_msg or "草稿" in err_msg:
                    print("  【问题分析】draft_id 无效或草稿不存在。")
                elif "auth" in err_msg or "登录" in err_msg:
                    print("  【问题分析】发布权限不足或Cookie失效。")
        else:
            print(f"  ❌ 发布请求HTTP错误: {publish_resp.status_code}")
            
    except Exception as e:
        print(f"  ❌ 发布请求异常: {e}")

if __name__ == "__main__":
    debug_full_flow()