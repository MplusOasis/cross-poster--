import requests
import json
import time
import re

class JuejinPublisher:
    """掘金平台发布器"""
    
    def __init__(self, cookie):
        """
        初始化掘金发布器
        
        参数:
            cookie (str): 掘金登录Cookie
        """
        self.cookie = cookie.strip()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Cookie': self.cookie,
            'Referer': 'https://juejin.cn/editor/drafts/new',
            'Origin': 'https://juejin.cn',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
    def verify_login(self):
        """验证Cookie是否有效"""
        print("[验证] 检查登录状态...")
        url = 'https://api.juejin.cn/user_api/v1/user/get'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('err_no') == 0:
                    user_info = data['data']
                    print(f"  ✅ 登录成功！用户: {user_info.get('user_name', '未知')}")
                    return True
                else:
                    print(f"  ❌ 登录失败: {data.get('err_msg', '未知错误')}")
                    return False
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ 验证请求异常: {e}")
            return False
    
    def get_categories(self):
        """获取文章分类列表"""
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
                    print(f"  ❌ 获取分类失败: {data.get('err_msg')}")
                    return []
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                return []
        except Exception as e:
            print(f"  ❌ 获取分类异常: {e}")
            return []
    
    def get_tags(self, category_id, limit=20):
        """获取指定分类下的标签"""
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
                    print(f"  ❌ 获取标签失败: {data.get('err_msg')}")
                    return []
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                return []
        except Exception as e:
            print(f"  ❌ 获取标签异常: {e}")
            return []
    
    def create_draft(self, article_data):
        """创建草稿"""
        print("[创建] 正在创建草稿...")
        url = 'https://api.juejin.cn/content_api/v1/article_draft/create'
        
        # 构建请求数据
        data = {
            'title': article_data.get('title', '未命名文章'),
            'mark_content': article_data.get('content', ''),
            'brief_content': self._generate_summary(article_data.get('content', '')),
            'category_id': article_data.get('category_id', '6809637767543259144'),
            'tag_ids': article_data.get('tag_ids', ['6809640408797167623']),
            'edit_type': 10,  # Markdown格式
            'link_url': '',
            'cover_image': '',
        }
        
        print(f"  标题: {data['title'][:30]}...")
        print(f"  分类ID: {data['category_id']}")
        print(f"  标签: {data['tag_ids']}")
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=15)
            result = response.json()
            
            print(f"[响应] 状态码: {response.status_code}")
            
            if result.get('err_no') == 0:
                draft_id = result['data']['article_id']
                print(f"  ✅ 草稿创建成功！草稿ID: {draft_id}")
                return {
                    'success': True,
                    'draft_id': draft_id,
                    'data': result['data']
                }
            else:
                print(f"  ❌ 草稿创建失败: {result.get('err_msg')}")
                return {
                    'success': False,
                    'error': result.get('err_msg'),
                    'code': result.get('err_no')
                }
                
        except Exception as e:
            print(f"  ❌ 创建草稿异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def publish_draft(self, draft_id, draft_info=None):
        """发布草稿"""
        print(f"[发布] 正在发布草稿 {draft_id}...")
        url = 'https://api.juejin.cn/content_api/v1/article/publish'
        
        # 构建发布数据
        data = {
            'draft_id': draft_id,
            'sync_to_org': False,
            'column_ids': [],
            'theme_ids': [],
            'encrypted_word_count': 0,  # 需要根据实际情况调整
            'origin_word_count': 100,   # 需要根据实际情况调整
        }
        
        # 如果提供了草稿信息，尝试从中获取字数信息
        if draft_info and 'word_count' in draft_info:
            data['origin_word_count'] = draft_info.get('word_count', 100)
        
        # 添加必要的查询参数
        params = {
            'aid': '2608',
            'uuid': 'auto_generated',  # 这应该从用户信息中获取
        }
        
        try:
            response = requests.post(url, headers=self.headers, params=params, json=data, timeout=15)
            result = response.json()
            
            print(f"[响应] 状态码: {response.status_code}")
            
            if result.get('err_no') == 0:
                article_id = result['data'].get('article_id')
                print(f"  ✅ 发布成功！文章ID: {article_id}")
                print(f"  文章链接: https://juejin.cn/post/{article_id}")
                return {
                    'success': True,
                    'article_id': article_id,
                    'url': f'https://juejin.cn/post/{article_id}'
                }
            else:
                error_msg = result.get('err_msg', '未知错误')
                print(f"  ❌ 发布失败: {error_msg}")
                
                # 提供具体的错误处理建议
                self._handle_publish_error(error_msg, data)
                return {
                    'success': False,
                    'error': error_msg,
                    'code': result.get('err_no')
                }
                
        except Exception as e:
            print(f"  ❌ 发布异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_summary(self, content, max_length=150):
        """从内容生成摘要"""
        # 移除Markdown标记
        clean_content = re.sub(r'[#*`~\[\]()]', '', content)
        clean_content = re.sub(r'!\[.*?\]\(.*?\)', '', clean_content)
        
        # 取前max_length个字符
        summary = clean_content.strip()[:max_length]
        
        # 如果内容太短，补充说明
        if len(summary) < 50:
            summary = "本文分享了技术相关的内容和经验总结..."
        
        return summary
    
    def _handle_publish_error(self, error_msg, request_data):
        """处理发布错误"""
        error_msg_lower = error_msg.lower()
        
        print("\n[诊断] 错误分析:")
        
        if 'cookie' in error_msg_lower or 'auth' in error_msg_lower or '登录' in error_msg:
            print("  ⚠️  Cookie失效或权限不足")
            print("  💡 请重新获取Cookie: ")
            print("     1. 在浏览器中登录掘金")
            print("     2. 按F12打开开发者工具")
            print("     3. 复制Network中任意请求的Cookie值")
            print("     4. 更新config.json文件")
            
        elif 'category' in error_msg_lower or '分类' in error_msg:
            print("  ⚠️  分类ID错误")
            print(f"  💡 当前分类ID: {request_data.get('category_id', '未设置')}")
            print("     请运行程序重新选择分类")
            
        elif 'tag' in error_msg_lower or '标签' in error_msg:
            print("  ⚠️  标签ID错误")
            print(f"  💡 当前标签: {request_data.get('tag_ids', [])}")
            print("     请运行程序重新选择标签")
            
        elif 'draft' in error_msg_lower or '草稿' in error_msg:
            print("  ⚠️  草稿ID错误或草稿不存在")
            print("  💡 请重新创建草稿")
            
        elif 'word' in error_msg_lower or '字数' in error_msg:
            print("  ⚠️  字数统计错误")
            print("  💡 需要正确计算encrypted_word_count和origin_word_count")
            
        elif '频繁' in error_msg or 'rate' in error_msg_lower:
            print("  ⚠️  操作过于频繁")
            print("  💡 请等待几分钟后重试")
            
        else:
            print(f"  ⚠️  未知错误类型: {error_msg}")
            print("  💡 请检查网络连接和参数格式")
    
    def publish_article(self, article_data):
        """
        完整的发布流程：验证登录 → 创建草稿 → 发布
        
        参数:
            article_data (dict): 包含标题、内容、分类ID、标签ID
        
        返回:
            dict: 发布结果
        """
        print("=" * 60)
        print("开始发布文章到掘金")
        print("=" * 60)
        
        # 1. 验证登录状态
        if not self.verify_login():
            return {'success': False, 'error': '登录验证失败'}
        
        # 2. 创建草稿
        draft_result = self.create_draft(article_data)
        if not draft_result['success']:
            return draft_result
        
        # 等待一会，避免请求过快
        time.sleep(2)
        
        # 3. 发布草稿
        publish_result = self.publish_draft(draft_result['draft_id'], draft_result.get('data'))
        
        return publish_result