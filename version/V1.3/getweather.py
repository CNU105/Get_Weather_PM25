﻿#coding=utf-8
#北京及周边省会城市污染数据、天气数据每小时监测值爬虫程序
import urllib.request
import re
import urllib.error
import time
import traceback
#模拟成浏览器
headers={"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
         "Accept-Encoding":"gbk,utf-8,gb2312",
         "Accept-Language":"zh-CN,zh;q=0.8",
         "User-Agent":"Mozilla/5.0(Windows NT 10.0; WOW64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
         "Connection":"keep-alive"}
opener=urllib.request.build_opener()
headall=[]
for key,value in headers.items():
    item=(key,value)
    headall.append(item)
opener.addheaders=headall
#将opener安装为全局
urllib.request.install_opener(opener)
def get_pm25_and_weather(city):
    #首先执行获取空气质量数据，返回数据更新时间
    data_time=getpm25(city)
    #然后将获取到的数据更新时间赋值给获取天气数据函数使用
    getweather(city,data_time)
def getpm25(city):
    try:
        #设置url地址
        url="http://pm25.in/"+city
        data=urllib.request.urlopen(url).read().decode("utf-8")
        print("城市："+city)
        #构建数据更新时间的表达式
        data_time='<div class="live_data_time">\s{1,}<p>数据更新时间：(.*?)</p>'
        #寻找出数据更新时间
        datatime=re.compile(data_time,re.S).findall(data)
        print("数据更新时间："+datatime[0])
        #构建数据收集的表达式
        data_pm25='<div class="span1">\s{1,}<div class="value">\n\s{1,}(.*?)\s{1,}</div>'
        data_o3='<div class="span1">\s{1,}<div class ="value">\n\s{1,}(.*?)\s{1,}</div>'
        #寻找出所有的监测值
        pm25list=re.compile(data_pm25,re.S).findall(data)
        o3list=re.compile(data_o3,re.S).findall(data)
        #将臭氧每小时的值插入到原列表中
        pm25list.append(o3list[0])
        print("AQI指数，PM2.5，PM10，CO，NO2，SO2，O3：（单位：μg/m3，CO为mg/m3）")
        print(pm25list)
        #将获取到的值写入文件中
        writefiles_pm25(city,datatime,pm25list)
        #返回数据更新时间值
        return datatime
    except urllib.error.URLError as e:
        print("获取空气质量数据函数出现URLERROR！两分钟后重试……")
        get_exception("获取空气质量数据异常", e)
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
        time.sleep(120)
        #出现异常则过一段时间重新执行此部分
        getpm25(city)
    except Exception as e:
        print("获取空气质量数据函数出现EXCEPTION！30秒钟后重试……")
        print("Exception："+str(e))
        get_exception("获取空气质量数据异常",e)
        time.sleep(30)
        # 出现异常则过一段时间重新执行此部分
        getpm25(city)
def writefiles_pm25(filename,datatime,pm25list):
    try:
        #将获取的数据写入文件中，数据分别为时间，AQI指数，PM2.5，PM10，CO，NO2，SO2，O3。（单位：μg/m3，CO为mg/m3）
        with open("D:\Python35\mydata\data_pm25\data_pm25_"+filename+".txt","a",errors="ignore") as f:
            f.write(str(datatime[0]))
            f.write(",")
            for pm25 in pm25list:
                f.write(str(pm25))
                f.write(",")
            f.write("\n")
        print("该条空气质量数据已添加到文件中！")
    except Exception as e:
        print("空气质量数据写入文件函数出现异常！将跳过此部分……")
        print("Exception："+str(e))
        traceback.print_exc()  #获得错误行数
        get_exception("空气质量数据写入文件异常",e)
        pass
def getweather(city,datatime):
    try:
        #构建url
        url="http://"+city+".tianqi.com/"
        data=urllib.request.urlopen(url).read().decode("gbk")
        #构建数据收集的表达式
        data_weather='<li class="cDRed">(.*?)</li>'
        data_wind='<li style="height:18px;overflow:hidden">(.*?)</li>'
        data_temperature='<div id="rettemp"><strong>(.*?)&deg'
        data_humidity='</strong><span>相对湿度：(.*?)</span>'
        #寻找出所有的监测值
        weatherlist=re.compile(data_weather,re.S).findall(data)
        windlist=re.compile(data_wind,re.S).findall(data)
        temperaturelist=re.compile(data_temperature,re.S).findall(data)
        humiditylist=re.compile(data_humidity,re.S).findall(data)
        #将其他值插入到天气列表中
        weatherlist.append(windlist[0])
        weatherlist.append(temperaturelist[0])
        weatherlist.append(humiditylist[0])
        print("天气状况，风向风速，实时温度，相对湿度：")
        print(weatherlist)
        #将获取到的值写入文件中
        writefiles_weather(city,datatime,weatherlist)
    except urllib.error.URLError as e:
        print("获取天气状况数据出现URLERROR！两分钟后重试……")
        get_exception("获取天气状况数据异常",e)
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
        time.sleep(120)
        #出现异常则过一段时间重新执行此部分
        getweather(city,datatime)
    except Exception as e:
        print("获取天气状况数据出现EXCEPTION！30秒钟后重试……")
        print("Exception："+str(e))
        get_exception("获取天气状况数据异常",e)
        time.sleep(30)
        # 出现异常则过一段时间重新执行此部分
        getweather(city,datatime)
def writefiles_weather(filename,datatime,weatherlist):
    try:
        #将获取的数据写入文件中，数据分别为时间，天气状况，风向风速，实时温度，相对湿度。
        with open("D:\Python35\mydata\data_weather\data_weather_"+filename+".txt","a",errors="ignore") as f:
            f.write(str(datatime[0]))
            f.write(",")
            for weather in weatherlist:
                f.write(str(weather))
                f.write(",")
            f.write("\n")
        print("该条天气数据已添加到文件中！")
    except Exception as e:
        print("天气状况数据写入文件函数出现异常！将跳过此部分……")
        print("Exception："+str(e))
        traceback.print_exc()  #获得错误行数
        get_exception("天气状况数据写入文件异常",e)
        pass
def get_exception(string,e):
    with open("D:\mydata\Error.txt","a",errors="ignore") as f:
        datetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        f.write(datetime+" 【"+string+"】"+str(e)+"\n")
    print("异常信息已经写入文档！")
#退出循环可用Ctrl+C键
while True:
    print("开始工作！")
    get_pm25_and_weather("beijing")
    get_pm25_and_weather("tianjin")
    get_pm25_and_weather("shijiazhuang")
    get_pm25_and_weather("taiyuan")
    get_pm25_and_weather("jinan")
    get_pm25_and_weather("shenyang")
    get_pm25_and_weather("huhehaote")
    get_pm25_and_weather("zhengzhou")
    #每一小时执行一次
    print("休息中……")
    print("\n")
    time.sleep(3600)