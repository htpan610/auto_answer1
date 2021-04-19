import re
import time
from PIL import Image
import pytesseract

from my_get_users import get_users
from myToTxt import toTxt

import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located


# https://zhuanlan.zhihu.com/p/111859925



class VerificationCode:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.find_element = self.driver.find_element_by_css_selector
        # 隐士等待超时设置为100s，100s还不出现要找的元素就报错了
        self.driver.implicitly_wait(5)


    def get_pictures(self):
        self.driver.save_screenshot('pictures.png')  # 全屏截图
        page_snap_obj = Image.open('pictures.png')
        img = self.driver.find_element_by_id("captcha_image")  # 验证码元素位置
        # time.sleep(1)
        location = img.location
        size = img.size  # 获取验证码的大小参数
        left = location['x'] + 3
        top = location['y'] + 5
        right = left + size['width'] - 10
        bottom = top + size['height']
        image_obj = page_snap_obj.crop((left, top, right, bottom))  # 按照验证码的长宽，切割验证码
        # image_obj.show()  # 打开切割后的完整验证码
        # self.driver.close()  # 处理完验证码后关闭浏览器
        return image_obj

    def processing_image(self):
        image_obj = self.get_pictures()  # 获取验证码
        img = image_obj.convert("L")  # 转灰度
        pixdata = img.load()
        w, h = img.size
        threshold = 160
        # 遍历所有像素，大于阈值的为黑色
        for y in range(h):
            for x in range(w):
                if pixdata[x, y] < threshold:
                    pixdata[x, y] = 0
                else:
                    pixdata[x, y] = 255
        return img

    def delete_spot(self):
        images = self.processing_image()
        data = images.getdata()
        w, h = images.size
        black_point = 0
        for x in range(1, w - 1):
            for y in range(1, h - 1):
                mid_pixel = data[w * y + x]  # 中央像素点像素值
                if mid_pixel < 50:  # 找出上下左右四个方向像素点像素值
                    top_pixel = data[w * (y - 1) + x]
                    left_pixel = data[w * y + (x - 1)]
                    down_pixel = data[w * (y + 1) + x]
                    right_pixel = data[w * y + (x + 1)]
                    # 判断上下左右的黑色像素点总个数
                    if top_pixel < 10:
                        black_point += 1
                    if left_pixel < 10:
                        black_point += 1
                    if down_pixel < 10:
                        black_point += 1
                    if right_pixel < 10:
                        black_point += 1
                    if black_point < 1:
                        images.putpixel((x, y), 255)
                    black_point = 0
        # images.show()
        return images

    def image_str(self, account, pw):
        image = self.delete_spot()
        # image.show()
        pytesseract.pytesseract.tesseract_cmd = r"D:\Program Files (x86)\Tesseract-OCR\tesseract.exe"  # 设置pyteseract路径
        result = pytesseract.image_to_string(image)  # 图片转文字\
        resultj = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", result)  # 去除识别出来的特殊字符
        result_four = resultj[0:4]  # 只获取前4个字符
        self.driver.find_element_by_id(id_="username").send_keys(account)
        self.driver.find_element_by_id(id_="password").send_keys(pw)
        time.sleep(0.2)
        self.driver.find_element_by_id(id_="captcha").send_keys(result_four)

        self.driver.find_element_by_id(id_="login_btn").click()
        now_url = self.driver.current_url
        if now_url == 'http://117.149.146.161:8081/phaj/login.jsp':
            return False
        else:
            return True

    def is_finished(self):
        try:
            self.driver.find_element_by_id("d_dialogEnt")
            return True
        except Exception as e:
            print(e)
            return False




    def toHomePage(self):
        self.driver.get('http://117.149.146.161:8081/phaj/login.jsp')



    def is_not_visible(self, locator, timeout=1000):
        try:
            ui.WebDriverWait(self.driver, timeout).until_not(EC.visibility_of_element_located((By.ID, locator)))
            return True
        except:
            return False

    def my_alert(self):
        dig_prompt = self.driver.switch_to.alert
        print(dig_prompt)

if __name__ == '__main__':
    # 1.获取所有账户
    users = get_users()
    print(users)
    ouzong = VerificationCode()
    ouzong.toHomePage()
    for i, user in enumerate(users):
        account = user['account']
        pw = user['pw']
        # 尝试登录，直到登录成功
        ddd=1
        while True:
            ddd+=1
            aa = ouzong.image_str(account, pw)
            #如果登录成功或者尝试登录超过7次，跳出循环
            if aa:
                break
            if ddd>7:
                users[i]['账号错误'] = '账号错误'
                break
        print('登录成功')
        # 如果没有答题，则手动答题，答题后跳转登录主页，进行下个循环
        # 如果已经答题，即没有‘答题’这个元素，则直接继续
        try:
            if not ouzong.is_finished():
                print('已经答过题了')
                users[i]['isAnswer'] = '答过题了'
                ouzong.toHomePage()
                continue
            else:
                print('没有答题，等待答题……')
                # 否则需要答题的话，就开始等待，直到答题界面消失，进入下一步
                if ouzong.is_not_visible(locator='d_dialogEnt'):
                    users[i]['isAnswer'] = '人工答题结束'
                    ouzong.toHomePage()
                    continue
        except:
            print('未知异常'+users[i]['name'])
    
            continue
    toTxt(users)
    print(users)
    # 如果已经答题，则直接跳转主页，进行下个循环
