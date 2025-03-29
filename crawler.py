import requests
import json
import csv
import time
import os
from typing import Dict, List
import re  # 新增正则模块导入

# 伪装浏览器请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': input('请从浏览器开发者工具复制完整Cookie: ')
}

def get_comments(bvid: str, keyword: str, max_page: int = 10) -> List[Dict]:
    """
    获取指定视频的包含关键词的评论
    :param bvid: 视频BV号
    :param keyword: 搜索关键词
    :param max_page: 最大爬取页数
    """
    comments = []
    session = requests.Session()
    
    for page in range(1, max_page + 1):
        url = f'https://api.bilibili.com/x/v2/reply/main'
        params = {
            'jsonp': 'jsonp',
            'next': page,
            'type': 1,
            'oid': bvid2oid(bvid),
            'mode': 3  # 按热门排序
        }

        try:
            response = session.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            data = json.loads(response.text)

            if data['code'] == 0:
                print(f'正在抓取第{page}页, 该页评论数：{len(data["data"]["replies"])}')
                if not data['data']['replies']:
                    print('已无更多评论，抓取结束')
                    break
                for reply in data['data']['replies']:
                    if keyword in reply['content']['message']:
                        comments.append({
                            'user': reply['member']['uname'],
                            'content': reply['content']['message'],
                            'like': reply['like'],
                            'time': time.strftime('%Y-%m-%d %H:%M:%S', 
                                time.localtime(reply['ctime']))
                        })
                print(f'第{page}页抓取完成，当前总数：{len(comments)}')
                time.sleep(1.5)  # 防止请求过快
            else:
                print(f'请求失败：{data["message"]}')
                break

        except Exception as e:
            print(f'发生错误：{str(e)}')
            break

    return comments

def get_oid_from_web(bvid: str) -> str:
    """通过网页源码获取oid的备用方案"""
    try:
        url = f'https://www.bilibili.com/video/{bvid}'
        headers = HEADERS.copy()
        headers['Referer'] = url
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 优化后的正则表达式精确匹配数字aid
        # 转义bvid中的特殊字符
        escaped_bvid = re.escape(bvid)
        aid_pattern = r'"aid":(?P<id>\d+),"bvid":"%s"' % escaped_bvid
        match = re.search(aid_pattern, response.text)
        if match:
            aid = match.group('id')
            print(f'网页获取成功：{bvid} -> aid={aid}')
            return aid
        raise ValueError('未找到匹配的aid')
    except Exception as e:
        print(f'网页获取失败：{str(e)}')
        raise


def bvid2oid(bvid: str) -> str:
    try:
        return get_oid_from_web(bvid)
    except Exception as web_err:
        raise RuntimeError(
            f'网页错误: {str(web_err)}'
        ) from web_err


def save_to_csv(comments: List[Dict], filename: str):
    """保存评论到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['user', 'content', 'like', 'time'])
        writer.writeheader()
        writer.writerows(comments)

def process_bvid_from_files():
    os.makedirs('comments', exist_ok=True)
    for filename in os.listdir('videos'):
        if filename.endswith('.txt'):
            mid = filename.split('.')[0]
            with open(os.path.join('videos', filename), 'r', encoding='utf-8') as f:
                for line in f:
                    bvid = line.strip()
                    if bvid.startswith('BV') and len(bvid) == 12:
                        result = get_comments(bvid, '鸡煲', 500)
                        csv_name = f'comments/bilibili_comments_{mid}_{bvid}.csv'
                        save_to_csv(result, csv_name)
                        print(f'已保存{len(result)}条评论到{csv_name}')

if __name__ == '__main__':
    choice = input('请选择模式：1.批量处理txt文件 2.手动输入BV号\n')
    if choice == '1':
        process_bvid_from_files()
    else:
        target_bvid = input('请输入视频BV号：')
        result = get_comments(target_bvid, '鸡煲', 500)
        save_to_csv(result, 'comments/bilibili_comments_' + str(target_bvid) + '.csv')
        print(f'共抓取到{len(result)}条相关评论')
    HEADERS['Cookie'] = 'SESSDATA=xxxxxx;'  # 添加默认测试cookie