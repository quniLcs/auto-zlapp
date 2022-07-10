# The original code is from https://github.com/FDUCSLG/pafd-automated
# The following has been optimized

# The log file can be sent to WeChat by PushPlus with reference to:
# https://github.com/DullSword/GLaDOS-CheckIn
# https://github.com/tyIceStream/GLaDOS_Checkin

# The python program has been packaged to an app with reference to:
# https://zhuanlan.zhihu.com/p/162237978


import time
import os
import logging

import string
import re
from json import loads

from getpass import getpass

import easyocr
import io
import numpy
from PIL import Image, ImageEnhance

import requests


def get_account(output = print):
    # The first way to get account: from the environment variables
    fudan_id = os.getenv("FUDAN_ID")
    fudan_password = os.getenv("FUDAN_PASSWORD")
    pushplus_token = os.getenv("PUSHPLUS_TOKEN")
    if fudan_id is not None and fudan_password is not None:
        output("Have obtained account information from the environmental variables.")
        return fudan_id, fudan_password, pushplus_token

    # The second way to get account: from the file
    if os.path.exists("account.txt"):
        output("Read the account information from account.txt.")
        with open("account.txt", "r") as account_file:
            text = account_file.readlines()

        fudan_id = text[0].split()[1].strip()
        fudan_password = text[1].split()[1].strip()
        pushplus_token = text[2].split()[1].strip()
        return fudan_id, fudan_password, pushplus_token

    else:  # The third way to get account: input
        output("account.txt not found.")
        output("Please input the following account information:")

        fudan_id = input("Fudan UIS ID: ")
        fudan_password = getpass("Fudan UIS Password: ")
        pushplus_token = input("PushPlus Token:")

        with open("account.txt", "w") as account_file:
            account_file.write("FUDAN_ID: %s\nFUDAN_PASSWORD: %s\nPUSHPLUS_TOKEN: %s\n" %
                               (fudan_id, fudan_password, pushplus_token))

        output("account.txt saved.")
        output("Please pay attention to the safety of the file.")
        output("A hyperlink to desktop is recommended.")

        return fudan_id, fudan_password, pushplus_token


def read_captcha(image):
    reader = easyocr.Reader(["en"])

    image = Image.open(io.BytesIO(image)).convert("L")
    image = ImageEnhance.Brightness(image).enhance(factor = 1.5)
    image = numpy.array(image)

    # without allow list, there may be unexpected spaces
    allowlist = list(string.ascii_letters)
    horizontal_list_agg, free_list_agg = reader.detect(image, optimal_num_chars=4)

    result = reader.recognize(image,
                              allowlist = allowlist,
                              horizontal_list = horizontal_list_agg[0],
                              free_list = free_list_agg[0],
                              detail = 0)
    return result[0]


class Fudan:
    # built a session with the server
    def __init__(self, fudan_id, fudan_password, pushplus_token,
                 login_url = "https://uis.fudan.edu.cn/authserver/login",
                 log_file = '', output = print):
        # the default value of login_url includes no service

        self.fudan_id = fudan_id
        self.fudan_password = fudan_password
        self.pushplus_token = pushplus_token
        self.login_url = login_url
        self.log_file = log_file
        self.output = output

        self.session = requests.session()

    def login_init(self):
        # check if the login page is open
        # if true, return the source code of the login page

        self.output("Start to open the login page.")
        login_page = self.session.get(self.login_url)

        if login_page.status_code == 200:
            self.output("Successfully open the login page.")
            self.output('')
            return login_page.text
        else:
            self.output("The status code is %d." % login_page.status_code)
            self.output("Fail to open the login page.")
            self.output("Check your Internet connection.")
            self.output('')
            self.close()

    def login(self):
        login_page_text = self.login_init()

        data = {"username": self.fudan_id, "password": self.fudan_password,
                "service": "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily"}
        data.update(re.findall(r'<input type="hidden" name="([a-zA-Z0-9\-_]+)" value="([a-zA-Z0-9\-_]+)"/?>',
                               login_page_text))

        self.output("Start to log in.")
        login_post = self.session.post(self.login_url, data = data, allow_redirects = False)

        if login_post.status_code == 302:
            self.output("Successfully log in.")
            self.output('')
        else:
            self.output("The status code is %d." % login_post.status_code)
            self.output("Fail to log in.")
            self.output("Please check the account information.")
            self.output('')
            self.close()

    def logout(self):
        self.output("Start to log out.")
        logout_url = "https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login"
        logout_page = self.session.get(logout_url)

        if "01-Jan-1970" in logout_page.headers.get("Set-Cookie"):
            self.output("Successfully log out.")
            self.output('')
        else:
            self.output("Exception arises when logging out.")
            self.output('')

    def send(self):
        with open(self.log_file, "r") as log_file:
            content = log_file.read()

        data = {"channel": "wechat", "token": self.pushplus_token,
                "title": "Auto-Zlapp Log File", "content": content}

        self.output('')
        self.output("Start to send message.")
        send_post = requests.post("https://www.pushplus.plus/send", data = data)
        send_json = send_post.json()

        if send_json["code"] == 200:
            self.output("Successfully send message.")
        else:
            self.output("Fail to send Message")

    def close(self):
        # log out, close the session and send message

        self.logout()

        self.session.close()
        self.output("Session closed.")

        if log_file:
            self.send()

        quit()


class Zlapp(Fudan):
    def check(self):
        self.output("Start to check the Fudan zlapp.")
        zlapp_page = self.session.get("https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info")
        zlapp_all_info = zlapp_page.json()

        zlapp_date = zlapp_all_info["d"]["info"]["date"]
        self.output("Last submit date: %s." % zlapp_date)

        zlapp_last_area = zlapp_all_info["d"]["oldInfo"]["area"]
        self.output("Last submit area: %s." % zlapp_last_area)

        if zlapp_last_area != "其他国家":
            zlapp_position = zlapp_all_info["d"]["info"]["geo_api_info"]
            zlapp_position = loads(zlapp_position)
            self.output("Last submit address: %s." % zlapp_position["formattedAddress"])

        today_date = time.strftime("%Y%m%d", time.localtime())
        self.output("Today's date: %s." % today_date)

        if zlapp_date == today_date:
            self.output("Submitted today.")
            self.output('')
            self.close()
        else:
            self.output("Not submitted today.")
            self.output('')
            self.zlapp_last_info = zlapp_all_info["d"]["oldInfo"]

    def submit(self):
        self.output("Start to submit.")

        while True:
            self.output("Start to read the captcha.")
            captcha_page = self.session.get("https://zlapp.fudan.edu.cn/backend/default/code")
            code = read_captcha(captcha_page.content)

            self.output("The captcha is: %s." % code)
            self.zlapp_last_info.update({"code": code})

            submit_post = self.session.post("https://zlapp.fudan.edu.cn/ncov/wap/fudan/save",
                                            data = self.zlapp_last_info, allow_redirects = False)

            submit_result = loads(submit_post.text)
            self.output("The result is: %s." % submit_result["m"])
            if submit_result["e"] != 1:
                break

        self.output('')


if __name__ == "__main__":
    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    log_path = "logs/"
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    logging.basicConfig(level = logging.INFO)
    log_file = "logs/%s.log" % time.strftime("%Y%m%d%H%M", time.localtime())
    log_handler = logging.FileHandler(log_file, mode = "w")
    log_formatter = logging.Formatter("%(asctime)s: %(message)s")
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(log_handler)

    fudan_id, fudan_password, pushplus_token = get_account(output = logger.info)
    login_url = "https://uis.fudan.edu.cn/authserver/login?service=https://zlapp.fudan.edu.cn/site/ncov/fudanDaily"

    zlapp = Zlapp(fudan_id, fudan_password, pushplus_token,
                  login_url = login_url, log_file = log_file, output = logger.info)

    zlapp.login()
    zlapp.check()
    zlapp.submit()
    zlapp.check()
    zlapp.close()
