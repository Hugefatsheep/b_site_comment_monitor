# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'FatSheep'
__time__ = '2020/9/19'
"""
# 快代理IP爬取 并建立可用IP池
import requests
import random
import time
from lxml import etree
from fake_useragent import UserAgent

ua = UserAgent(use_cache_server=False)
headers = {'User-Agent': ua.chrome}
http_proxies = []  # 全IP容器
uesful_ip_pool = []  # 有用IP容器
uesless_ip_pool = []  # 无用IP容器
# 350
with open("proxy.txt", "r") as f:
    all_ip = f.readlines()


def get_new_ip():
    proxy_ip = random.choice(all_ip)[:-1]
    new_ip = {'HTTP': proxy_ip}
    return new_ip


# proxy={'http':'IP:PORT'}
def ip_spider():  # 填写需要爬取IP的页数
    n = int(input('请输入需要爬取的页数：'))
    for a in range(n - 49, n + 1):
        proxy = get_new_ip()
        url = f'https://www.kuaidaili.com/free/inha/{a}/'
        try:
            response = requests.get(url, headers=headers, proxies=proxy)
        except ConnectionError:
            print("connect error!")
            break
        except TimeoutError:
            print("connect error!")
            break
        except requests.exceptions.ConnectionError:
            print("connect error!")
            break
        # 判断请求状态
        if response.status_code == 200:
            html_str = response.text
            re_tree = etree.HTML(html_str)
            ips_list = re_tree.xpath('//td[@data-title="IP"]/text()')
            types_list = re_tree.xpath('//td[@data-title="类型"]/text()')
            ports_list = re_tree.xpath('//td[@data-title="PORT"]/text()')

            print(ips_list)

            for i in list(zip(types_list, ips_list, ports_list)):
                ip_port = i[1] + ':' + i[2]
                ip_dic = {i[0]: ip_port}
                http_proxies.append(ip_dic)
        if a % 5 == 0:
            time.sleep(3)


def check_ip():  # 定义IP检测
    for proxy in http_proxies:
        url = 'https://www.baidu.com/'
        response = requests.get(url, headers=headers, proxies=proxy)
        if response.status_code == 200:
            uesful_ip_pool.append(proxy)
        else:
            uesless_ip_pool.append(proxy)


ip_spider()
check_ip()
with open("proxy_2.txt", "a") as fp:
    for ip_address in uesful_ip_pool:
        fp.write(ip_address["HTTP"] + "\n")

print(f'有{len(uesful_ip_pool)}个可用IP，可用IP池列表为\n{uesful_ip_pool}')
print('**************')
print(f'有{len(uesless_ip_pool)}个无用IP，无用IP池列表为\n{uesless_ip_pool}')
