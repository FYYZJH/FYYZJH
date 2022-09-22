from datetime import date, datetime, timedelta
import math
import time
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import configparser
from bs4 import BeautifulSoup
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  return weather['weather'], math.floor(weather['temp'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

def get_weekday():
    #日期时间
    date=(datetime.now()+timedelta(hours=8)).strftime("%Y-%m-%d %X")
    #星期
    dayOfWeek = (datetime.now()+timedelta(hours=8)).weekday()
    if dayOfWeek==0:
        weekd=date+"  星期一\n"
    if dayOfWeek==1:
        weekd=date+"  星期二\n"
    if dayOfWeek==2:
        weekd=date+"  星期三\n"
    if dayOfWeek==3:
        weekd=date+"  星期四\n"
    if dayOfWeek==4:
        weekd=date+"  星期五\n"
    if dayOfWeek==5:
        weekd=date+"  星期六\n"
    if dayOfWeek==6:
        weekd=date+"  星期日\n"
    return weekd

def top_mv():
    # 1 爬取源
    url = "https://movie.douban.com/chart"
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }

    # 2 发起http请求
    spond = requests.get(url, headers=header)
    res_text = spond.text
    # 3 内容解析
    soup = BeautifulSoup(res_text, "html.parser")
    soup1 = soup.find_all(width="75")  # 解析出电影名称
    # print(soup1[0]['alt'])
    soup2 = soup.find_all('span', class_="rating_nums")  # 解析出评分
    # print(soup2[0].text)
    # 4数据的处理

    """简单处理1，输入数值N，返回排第N的电影名及评分"""

    """处理2，将电影名和评分组成[{电影名：评分},{:}]的形式"""
    list_name = []  # 将电影名做成一个列表
    for i in range(10):
        list_name.append(soup1[i]['alt'])

    list_value = []  # 将评分值做成一个列表
    for i in range(10):
        list_value.append(soup2[i].text)

    dict_name_value = dict(zip(list_name, list_value))  # 将两个list转化为字典dict

    mv_top = sorted(dict_name_value.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)  # 字典排序,type==list


    for i in range(0,1):
        mv_top_name = mv_top[i][0]  # 取出电影名,后期直接使用
        mv_top_value = mv_top[i][1]  # 取出评分，后期直接使用
        show=str(mv_top_name) + ":" + str(mv_top_value) + "分"

    return show
  
 
client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature = get_weather()

sid=""
if temperature>=25:
  sid="[室外温度较高，注意喝水哦]"
elif temperature<=20:
  sid="[室外温度过低，记得多穿点衣服保暖]"
else:
  sid="[温度不高不低，但也要注意及时补水哦]"
  
data = {"weather":{"value":wea,"color":get_random_color()},"daytime":{"value":get_weekday(),"color":get_random_color()},"sid":{"value":sid,"color":get_random_color()},"temperature":{"value":str(temperature)+"℃","color":get_random_color()},"love_days":{"value":get_count(),"color":get_random_color()},"birthday_left":{"value":get_birthday(),"color":get_random_color()},"words":{"value":get_words(), "color":get_random_color()},"mv":{"value":top_mv(),"color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
