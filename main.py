# The original code is from https://github.com/FDUCSLG/pafd-automated
# The following has been optimized

import time
from os import path as osp, getenv

import string
import re
from json import loads

from getpass import getpass

import easyocr
import io
import numpy
from PIL import Image, ImageEnhance

from requests import adapters, session


def read_captcha(image):
    reader = easyocr.Reader(['en'])

    image = Image.open(io.BytesIO(image)).convert('L')
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
    def __init__(self, uid, psw, login_url = 'https://uis.fudan.edu.cn/authserver/login'):
        # the default value of url_login includes no service

        self.uid = uid
        self.psw = psw
        self.login_url = login_url

        self.session = session()

    def login_init(self):
        # check if the login page is open
        # if true, return the source code of the login page

        print("Start to open the login page.")
        login_page = self.session.get(self.login_url)

        if login_page.status_code == 200:
            print("Successfully open the login page.")
            print()
            return login_page.text
        else:
            print("The status code is %d." % login_page.status_code)
            print("Fail to open the login page.")
            print("Check your Internet connection.")
            print()
            self.close()

    def login(self):
        login_page_text = self.login_init()

        data = {"username": self.uid, "password": self.psw,
                "service": "https://zlapp.fudan.edu.cn/site/ncov/fudanDaily"}
        data.update(re.findall(r'<input type="hidden" name="([a-zA-Z0-9\-_]+)" value="([a-zA-Z0-9\-_]+)"/?>',
                               login_page_text))

        print("Start to log in.")
        login_post = self.session.post(self.login_url, data = data, allow_redirects = False)

        if login_post.status_code == 302:
            print("Successfully log in.")
            print()
        else:
            print("The status code is %d." % login_post.status_code)
            print("Fail to log in.")
            print("Please check the account information.")
            print()
            self.close()

    def logout(self):
        print("Start to log out.")
        logout_url = 'https://uis.fudan.edu.cn/authserver/logout?service=/authserver/login'
        logout_page = self.session.get(logout_url)

        if '01-Jan-1970' in logout_page.headers.get('Set-Cookie'):
            print("Successfully log out.")
            print()
        else:
            print("Exception arises when logging out.")
            print()

    def close(self):
        # log out and close the session

        self.logout()
        self.session.close()
        print("Session closed.")

        exit()


class Zlapp(Fudan):
    def check(self):
        print("Start to check the Fudan zlapp.")
        zlapp_page = self.session.get('https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info')
        zlapp_all_info = zlapp_page.json()

        zlapp_date = zlapp_all_info["d"]["info"]["date"]
        print("Last submit date: %s." % zlapp_date)

        zlapp_last_area = zlapp_all_info["d"]["oldInfo"]["area"]
        print("Last submit area: %s." % zlapp_last_area)

        if zlapp_last_area != "其他国家":
            zlapp_position = zlapp_all_info["d"]["info"]['geo_api_info']
            zlapp_position = loads(zlapp_position)
            print("Last submit address: %s." % zlapp_position['formattedAddress'])

        # Adapt the time zone
        # os.environ['TZ'] = 'Asia/Shanghai'
        # time.tzset()

        today_date = time.strftime("%Y%m%d", time.localtime())
        print("Today's date: %s." % today_date)

        if zlapp_date == today_date:
            print("Submitted today.")
            print()
            self.close()
        else:
            print("Not submitted today.")
            print()
            self.zlapp_last_info = zlapp_all_info["d"]["oldInfo"]

    def submit(self):
        print("Start to submit.")

        while True:
            print("Start to read the captcha.")
            captcha_page = self.session.get("https://zlapp.fudan.edu.cn/backend/default/code")
            code = read_captcha(captcha_page.content)

            print("The captcha is: %s." % code)
            self.zlapp_last_info.update({"code": code})

            submit_post = self.session.post('https://zlapp.fudan.edu.cn/ncov/wap/fudan/save',
                                            data = self.zlapp_last_info, allow_redirects = False)

            submit_result = loads(submit_post.text)
            print("The result is: %s." % submit_result["m"])
            if submit_result["e"] != 1:
                break

        print()


def get_account():
    # The first way to get account: from the environment variables
    uid = getenv("FUDAN_ID")
    psw = getenv("FUDAN_PASSWORD")
    if uid is not None and psw is not None:
        print("Have obtained id and password from the environmental variables.")
        return uid, psw

    # The second way to get account: from the file
    if osp.exists("account.txt"):
        print("Read the id and password from account.txt.")
        with open("account.txt", "r") as file:
            text = file.readlines()

        if text[0][:4] != "ID: " or len(text[0]) < 10:
            print("Error in account.txt.")
            exit()

        uid = text[0].split()[1].strip()
        psw = text[1].split()[1].strip()
        return uid, psw

    else:  # The third way to get account: input
        print("account.txt not found.")
        print('Please input the id and password.')

        uid = input("ID: ")
        psw = getpass("PASSWORD: ")

        with open("account.txt", "w") as file:
            file.write("ID: %s\nPASSWORD: %s\n" % (uid, psw))

        print("account.txt saved.")
        print("Please pay attention to the safety of the file.")
        print("A hyperlink to desktop is recommended.")

        return uid, psw


if __name__ == '__main__':
    adapters.DEFAULT_RETRIES = 5

    uid, psw = get_account()
    login_url = 'https://uis.fudan.edu.cn/authserver/login?service=https://zlapp.fudan.edu.cn/site/ncov/fudanDaily'

    zlapp = Zlapp(uid, psw, login_url = login_url)
    zlapp.login()
    zlapp.check()
    zlapp.submit()
    zlapp.check()
    zlapp.close()
