# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'FatSheep'
__time__ = '2020/9/19'
"""
import requests
import random
import json
import time
from fake_useragent import UserAgent
import pymysql

# https://api.bilibili.com/x/web-interface/newlist?rid=121&type=1&pn=5&ps=248900 分区视频BV号
# B站API详情 https://github.com/SocialSisterYi/bilibili-API-collect

# B站分区tID
subarea_list = [1, 24, 25, 47, 86, 27, 13, 33, 32, 51, 152, 167, 153, 168, 169, 195, 170, 3, 28, 31, 30, 194, 59, 193,
                29, 130, 129, 20, 198, 199, 200, 154, 156, 4, 17, 171, 172, 65, 173, 121, 136, 19, 36, 201, 124, 207,
                208, 209, 122, 188, 95, 189, 190, 191, 160, 138, 21, 76, 75, 161, 162, 163, 176, 174, 119, 22, 26, 126,
                127, 155, 157, 158, 164, 159, 192, 202, 203, 204, 205, 206, 5, 71, 137, 131, 181, 182, 183, 85, 184,
                177, 37, 178]

# 视频AV/BV号列表
aid_list = []
bvid_list = []

# 评论用户及其信息
info_list = []

# 获取失败AV号
failed_list = []

dir_name = ""

useragent = UserAgent(use_cache_server=False)
headers = {'User-Agent': useragent.chrome}
with open("proxy_2.txt", "r") as f:
    all_ip = f.readlines()


# 获取指定分区的所有视频的BV号 rid:分区编号 size:单次拉取数目 page:页数
def getAllAVList(rid, day):  # page_start, page_end, size
    # 获取分区视频列表
    proxy = get_new_ip()  # 获取代理ip
    url = "http://api.bilibili.com/x/web-interface/ranking/region?rid=" + str(rid) + "&day=" + str(day)
    text = requests.get(url, proxies=proxy, headers=headers).text
    json_text = json.loads(text)
    # 遍历JSON格式信息，获取视频aid
    if json_text["code"] == 0:
        for item in json_text["data"]:
            aid_list.append(item["aid"])
            bvid_list.append(item["bvid"])
    else:
        print("Be banned!!!!!")
        print(str(rid))
        return 0
    return 0


# 获取一个AV号视频下所有评论
def getAllCommentList(order):
    item = aid_list[order]
    BV_order = bvid_list[order]
    proxy = get_new_ip()  # 获取代理ip
    url = "http://api.bilibili.com/x/web-interface/view?aid=" + str(item)
    numtext = requests.get(url, proxies=proxy, headers=headers).text
    json_text = json.loads(numtext)
    commentsNum = json_text["data"]["stat"]["reply"]
    page = commentsNum // 20 + 1
    for n in range(1, page):
        proxy = get_new_ip()
        url = "http://api.bilibili.com/x/v2/reply?type=1&oid=" + str(item) + "&pn=" + str(n)
        text = requests.get(url, proxies=proxy, headers=headers).text
        json_text_list = json.loads(text)
        try:
            for i in json_text_list["data"]["replies"]:
                info_list.append([BV_order, i["member"]["uname"], i["content"]["message"], str(i["ctime"])])
        except TypeError:
            failed_list.append(item)
            print("评论访问被拒绝")
            return 0
        if n % 5 == 0:
            time.sleep(2.2)
    return 1
    # print(info_list)


# 保存评论进数据库
def saveTxt(filename, filecontent):
    if filecontent:
        for content in filecontent:
            if content[0] != '':
                connection = pymysql.connect(
                    host='locakhost',
                    user='root',
                    passwd='Pass123456@',
                    database='blbl',
                    charset='utf8mb4'
                )
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO daily(id, bvnum, username, content, date) VALUES (NULL, '%s', '%s', '%s', '%s')" %
                    (content[0], content[1], content[2], get_time(int(content[3]))))
                cursor.close()
    else:
        print(str(filename) + "无评论。")
        return 0


def get_time(now):
    transed_time = time.localtime(now)
    real_time = time.strftime("%Y-%m-%d %H:%M:%S", transed_time)
    return real_time


def get_new_ip():
    proxy_ip = random.choice(all_ip)[:-1]
    new_ip = {'HTTP': proxy_ip}
    return new_ip


if __name__ == "__main__":
    for code in range(0, len(subarea_list) - 1):
        aid_list.clear()
        bvid_list.clear()
        getAllAVList(subarea_list[code], 3)  # rid,page_start,page_end,size
        count = 0
        for order in range(0, len(aid_list) - 1):
            info_list.clear()
            getAllCommentList(order)
            saveTxt(bvid_list[count], info_list)
            count += 1
            time.sleep(1)
        with open("failed.txt", "a", encoding='utf-8') as fp:
            for title in failed_list:
                fp.write(str(title) + "\n")
