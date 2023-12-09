import requests
import datetime
import threading
import random
import json
import os
import sys

class GladosCheckin:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }# Cookie是签到URL的Cookie
        self.data = {"token": "glados.one"}
        self.URL_checkin = "https://glados.rocks/api/user/checkin"
        self.URL_status = "https://glados.rocks/api/user/status"
        self.SendKey = None
        self.Period = None# 运行周期，单位小时

    # 写入日志并打印
    def write_log(self, text):
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")
        print(text)
        print("\n")
    
    # 方糖消息推送
    def send_message_fangtang(self, text, desp):
        data = {
            "text": text,# 标题
            "desp": desp# description，不是标题是内容
        }
        response = requests.post(f"https://sc.ftqq.com/{self.SendKey}.send", data=data)
        self.write_log(f"   方糖({self.SendKey}): {response.text}")

    # 签到脚本
    def crawling(self):
        self.write_log(str(datetime.datetime.now()))
        r_checkin = requests.post(self.URL_checkin, headers=self.headers, data=self.data)
        r_status = requests.get(self.URL_status, headers=self.headers)
        data_checkin = r_checkin.json()
        data_status = r_status.json()
        send_data = f"points: {data_checkin['points']}. \nmessage: {data_checkin['message']}. \nleft days: {data_status['data']['leftDays']}. "
        self.write_log(send_data)
        self.send_message_fangtang("GladosCheckin", send_data)
        self.write_log("\n")

    # 定时执行（实际是隔随机时间执行）
    def func_timer(self):
        random_time = random.uniform(-1800,1800)# 小数的秒数，更不容易被发现
        
        try:
            self.crawling()
        except Exception:
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,
            }
            self.write_log(str(exc_dict))

        # 定时器构造函数主要有2个参数，第一个参数为时间，第二个参数为函数名
        self.timer = threading.Timer(self.Period*3600+random_time, self.func_timer)   # 每过一段随机时间（单位：秒）调用一次函数

        self.timer.start()    #启用定时器

    # 初始化并开始爬虫   
    def crawler_start(self):
        # 新建log文件
        with open("log.txt", "w"):
            pass
        # 读取文件数据
        with open("config.json", 'r', encoding="utf-8") as f:
            user_data = json.load(f)
        self.headers["Cookie"] = user_data["Cookie"]
        self.SendKey = user_data["SendKey"]
        self.Period = user_data["Period"]

        self.timer = threading.Timer(1, self.func_timer)
        self.timer.start()
        print("Crawler starts...")

if __name__ == "__main__":
    glados_checkin = GladosCheckin()
    glados_checkin.crawler_start()