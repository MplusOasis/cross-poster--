def get_categories(self):
    """获取文章分类列表（支持失败时返回空列表）"""
    print("[获取] 正在获取分类列表...")
    url = 'https://api.juejin.cn/tag_api/v1/query_category_briefs'
    
    try:
        response = requests.get(url, headers=self.headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('err_no') == 0:
                categories = data['data']
                print(f"  ✅ 获取到 {len(categories)} 个分类")
                return categories
            else:
                print(f"  ⚠️  API返回错误: {data.get('err_msg')}")
                return []  # 返回空列表，触发离线模式
        else:
            print(f"  ⚠️  HTTP错误: {response.status_code}")
            return []  # 返回空列表，触发离线模式
    except requests.exceptions.Timeout:
        print("  ⚠️  请求超时，API可能不可用")
        return []  # 返回空列表，触发离线模式
    except requests.exceptions.ConnectionError:
        print("  ⚠️  网络连接错误，API不可用")
        return []  # 返回空列表，触发离线模式
    except Exception as e:
        print(f"  ⚠️  获取分类异常: {e}")
        return []  # 返回空列表，触发离线模式

def get_tags(self, category_id, limit=20):
    """获取指定分类下的标签（支持失败时返回空列表）"""
    print(f"[获取] 正在获取分类下的标签...")
    url = 'https://api.juejin.cn/tag_api/v1/query_tag_list'
    
    payload = {
        'cursor': '0',
        'limit': limit,
        'sort_type': 200,  # 按热门排序
        'category_id': category_id
    }
    
    try:
        response = requests.post(url, headers=self.headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('err_no') == 0:
                tags = data['data']
                print(f"  ✅ 获取到 {len(tags)} 个标签")
                return tags
            else:
                print(f"  ⚠️  API返回错误: {data.get('err_msg')}")
                return []  # 返回空列表，触发离线模式
        else:
            print(f"  ⚠️  HTTP错误: {response.status_code}")
            return []  # 返回空列表，触发离线模式
    except requests.exceptions.Timeout:
        print("  ⚠️  请求超时，API可能不可用")
        return []  # 返回空列表，触发离线模式
    except requests.exceptions.ConnectionError:
        print("  ⚠️  网络连接错误，API不可用")
        return []  # 返回空列表，触发离线模式
    except Exception as e:
        print(f"  ⚠️  获取标签异常: {e}")
        return []  # 返回空列表，触发离线模式