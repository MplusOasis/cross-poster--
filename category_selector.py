import json
from platforms.juejin import JuejinPublisher

class CategorySelector:
    """交互式分类标签选择器"""
    
    def __init__(self, cookie):
        self.publisher = JuejinPublisher(cookie)
    
    def select_category_interactive(self):
        """交互式选择分类"""
        print("\n" + "="*50)
        print("请选择文章分类")
        print("="*50)
        
        # 获取分类列表
        categories = self.publisher.get_categories()
        
        if not categories:
            print("⚠️  无法获取分类列表，使用默认分类")
            return {
                'category_id': '6809637767543259144',
                'category_name': '后端'
            }
        
        # 显示分类选项
        for i, cat in enumerate(categories, 1):
            cat_name = cat.get('category_name', '未知分类')
            cat_id = cat.get('category_id', '')
            print(f"{i:2d}. {cat_name}")
        
        print("-"*50)
        
        # 用户选择
        while True:
            try:
                choice = input(f"请输入分类编号 (1-{len(categories)}): ").strip()
                if not choice:
                    print("⚠️  请输入编号")
                    continue
                    
                choice_num = int(choice)
                if 1 <= choice_num <= len(categories):
                    selected = categories[choice_num-1]
                    return {
                        'category_id': selected.get('category_id'),
                        'category_name': selected.get('category_name')
                    }
                else:
                    print(f"⚠️  请输入1-{len(categories)}之间的数字")
            except ValueError:
                print("⚠️  请输入有效的数字")
            except KeyboardInterrupt:
                print("\n👋 用户取消选择")
                return None
    
    def select_tags_interactive(self, category_id):
        """交互式选择标签"""
        print("\n" + "="*50)
        print("请选择文章标签（至少1个，最多5个）")
        print("="*50)
        
        # 获取标签列表
        tags = self.publisher.get_tags(category_id)
        
        if not tags:
            print("⚠️  无法获取标签列表，使用默认标签")
            return ['6809640408797167623']  # 后端标签
        
        # 显示标签选项
        for i, tag in enumerate(tags, 1):
            tag_name = tag.get('tag_name', '未知标签')
            tag_id = tag.get('tag_id', '')
            print(f"{i:2d}. {tag_name}")
        
        print("-"*50)
        print("提示：可以输入多个编号，用逗号分隔，如：1,3,5")
        
        # 用户选择
        selected_tag_ids = []
        while len(selected_tag_ids) < 5:  # 掘金最多5个标签
            try:
                if selected_tag_ids:
                    print(f"\n已选择标签: {len(selected_tag_ids)}个")
                
                choice = input(f"请输入标签编号 (输入0完成选择): ").strip()
                
                if choice == '0':
                    if len(selected_tag_ids) == 0:
                        print("⚠️  至少需要选择1个标签")
                        continue
                    break
                
                # 处理多个选择
                choices = [c.strip() for c in choice.split(',')]
                
                for c in choices:
                    if not c:
                        continue
                        
                    choice_num = int(c)
                    if 1 <= choice_num <= len(tags):
                        tag = tags[choice_num-1]
                        tag_id = tag.get('tag_id')
                        tag_name = tag.get('tag_name')
                        
                        if tag_id not in selected_tag_ids:
                            selected_tag_ids.append(tag_id)
                            print(f"  ✅ 已选择: {tag_name}")
                        else:
                            print(f"  ⚠️  {tag_name} 已选择")
                    else:
                        print(f"  ⚠️  编号 {c} 无效，请输入1-{len(tags)}之间的数字")
                
                if len(selected_tag_ids) >= 5:
                    print("⚠️  已达到最大标签数(5个)")
                    break
                    
            except ValueError:
                print("⚠️  请输入有效的数字")
            except KeyboardInterrupt:
                print("\n👋 用户取消选择")
                return None
        
        return selected_tag_ids
    
    def get_default_categories(self):
        """获取默认分类（当API不可用时使用）"""
        return [
            {'category_id': '6809637767543259144', 'category_name': '后端'},
            {'category_id': '6809637769959178254', 'category_name': '前端'},
            {'category_id': '6809635626879549454', 'category_name': 'Android'},
            {'category_id': '6809635626661445640', 'category_name': 'iOS'},
            {'category_id': '6809637773935378440', 'category_name': '人工智能'},
            {'category_id': '6809637771511070734', 'category_name': '开发工具'},
            {'category_id': '6809637776263217160', 'category_name': '代码人生'},
            {'category_id': '6809637772874219534', 'category_name': '阅读'},
        ]
    
    def get_default_tags(self):
        """获取默认标签（当API不可用时使用）"""
        return {
            '后端': ['6809640408797167623', '6809640407484334093'],
            '前端': ['6809640402101166094', '6809640398105870343'],
            'Python': ['6809640407484334093'],
            'Java': ['6809640404791590919'],
            'JavaScript': ['6809640402101166088'],
            'GitHub': ['6809640501776482317'],
        }