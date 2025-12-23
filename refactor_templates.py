
import os
import re

TEMPLATE_DIR = 'templates'

REPLACEMENTS = {
    r"url_for\('login'": "url_for('auth.login'",
    r"url_for\('logout'": "url_for('auth.logout'",
    r"url_for\('register'": "url_for('auth.register'",
    
    r"url_for\('index'": "url_for('main.index'",
    r"url_for\('dashboard'": "url_for('main.dashboard'",
    r"url_for\('seller_profile'": "url_for('main.seller_profile'",
    r"url_for\('edit_my_profile'": "url_for('main.edit_my_profile'",
    r"url_for\('contact'": "url_for('main.contact'",
    r"url_for\('about'": "url_for('main.about'",
    r"url_for\('blog'": "url_for('main.blog'",
    
    r"url_for\('manage_users'": "url_for('admin.manage_users'",
    r"url_for\('create_user'": "url_for('admin.create_user'",
    r"url_for\('edit_user'": "url_for('admin.edit_user'",
    r"url_for\('manage_categories'": "url_for('admin.manage_categories'",
    r"url_for\('delete_category'": "url_for('admin.delete_category'",
    r"url_for\('manage_banners'": "url_for('admin.manage_banners'",
    r"url_for\('delete_banner'": "url_for('admin.delete_banner'",
    r"url_for\('toggle_banner'": "url_for('admin.toggle_banner'",
    r"url_for\('delete_user'": "url_for('admin.delete_user'",
    r"url_for\('toggle_verification'": "url_for('admin.toggle_verification'",
    
    r"url_for\('create_product'": "url_for('product.create_product'",
    r"url_for\('edit_product'": "url_for('product.edit_product'",
    r"url_for\('delete_product'": "url_for('product.delete_product'",
    r"url_for\('product_detail'": "url_for('product.product_detail'",
    r"url_for\('delete_product_image'": "url_for('product.delete_product_image'",
}

def refactor():
    print("Starting template refactor...")
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for pattern, replacement in REPLACEMENTS.items():
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {file}")
                else:
                    print(f"Skipped {file} (no changes)")

if __name__ == "__main__":
    refactor()
