import requests
import json
import os
import random
import time
import wbi

def get_bvid_list(mid):
    base_url = 'https://api.bilibili.com/x/space/wbi/arc/search'
    page = 1
    bvids = []
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Origin': 'https://space.bilibili.com',
            'Connection': 'keep-alive',
            'Referer': 'https://space.bilibili.com/546195/fans/fans',
            'Cache-Control': 'max-age=0',
            'cookie': input("请输入你的cookie: ")  # 替换为你的cookie，确保包含SESSDATA和bili_jct，否则可能无法访问视频列表
    }
    
    while True:
        img_key, sub_key = wbi.getWbiKeys()
        signed_params = wbi.encWbi(
            params={
                'mid': mid,
                'pn': page,
                'ps': 40,
            },
            img_key=img_key,
            sub_key=sub_key
        )
        
        session = requests.Session()
        session.headers.update(headers)
        
        try:
            time.sleep(5 + random.random()*2)  # 调整为5-7秒随机延迟
            response = session.get(base_url, params=signed_params)
            response.raise_for_status()
            print(f'响应状态码：{response.status_code}')
            print(f'响应内容：{response.text[:200]}...')  # 截取部分内容避免过长
            data = json.loads(response.text)
            
            if data['code'] != 0 or not data['data']['list']['vlist']:
                break
                
            for video in data['data']['list']['vlist']:
                bvids.append(video['bvid'])
                
            page += 1
            
        except Exception as e:
            print(f"请求失败: {e}")
            if page < 3:  # 前3页失败时重试
                print(f"第{page}页请求失败，5秒后重试...")
                time.sleep(5)
                continue
            break
            
    return bvids

def save_bvids(mid, bvids):
    os.makedirs('videos', exist_ok=True)
    filename = f'videos/{mid}.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(bvids))
    print(f"已保存{len(bvids)}个BV号到{filename}")

if __name__ == '__main__':
    try:
        mid = int(input("请输入B站UP主的MID: "))
        bvids = get_bvid_list(mid)
        save_bvids(mid, bvids)
    except ValueError:
        print("输入错误，请输入有效的数字MID")