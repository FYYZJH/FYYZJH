from datetime import date, datetime, timedelta
import math
import time
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import configparser
from BeautifulSoup4 import BeautifulSoup
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
  
data = {"weather":{"value":wea},"daytime":{"value":get_weekday()},"temperature":{"value":str(temperature)+"℃"},"love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},"words":{"value":get_words(), "color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
