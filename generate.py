import os
import requests
import jinja2
from datetime import datetime

# 配置飞书API（从GitHub Secrets获取）
APP_ID = os.environ['FEISHU_APP_ID']
APP_SECRET = os.environ['FEISHU_APP_SECRET']
APP_TOKEN = os.environ['FEISHU_APP_TOKEN']
TABLE_ID = os.environ['FEISHU_TABLE_ID']

# 获取访问令牌
def get_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, headers=headers, json=data)
    return response.json()['tenant_access_token']

# 获取表格数据
def fetch_news():
    token = get_access_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    records = response.json()['data']['items']
    
    news_list = []
    for item in records:
        fields = item['fields']
        news_list.append({
            "id": item['record_id'],
            "title": fields.get('标题'),
            "content": fields.get('内容'),
            "date": fields.get('发布日期'),
            "url_name": fields.get('URL名称')
        })
    return sorted(news_list, key=lambda x: x['date'], reverse=True)

# 生成静态页面
def generate_pages(news_list):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    
    # 生成首页
    index_template = env.get_template('index.html')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_template.render(news_list=news_list))
    
    # 生成详情页
    os.makedirs('posts', exist_ok=True)
    post_template = env.get_template('post.html')
    for news in news_list:
        filename = f"posts/{news['url_name']}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(post_template.render(news=news))

if __name__ == "__main__":
    news_data = fetch_news()
    generate_pages(news_data)
    print(f"Generated {len(news_data)} news pages")
