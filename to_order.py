import requests
import execjs
import time
import pytesseract

from PIL import Image, ImageEnhance, ImageFilter
from collections import defaultdict
from aip import AipOcr
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed
from requests.adapters import HTTPAdapter


class gzairports():
    order_url = "http://www.gzairports.com:11111/"
    # 查询到预设参数
    appointmentSettings = list()
    # token
    token = ""
    validate_code = ""

    start_station = ""
    end_station = ""

    _BAIDU_API_KEY = "vhYCS7fDeMZ7VypFOF64MFo4"
    _BAIDU_APP_ID = "17717357"
    _BAIDU_SECRET_KEY = "hcRXcIu7Una7MZIMv87vNIKXKlIPYLsF"

    def __init__(self):
        with open("cipher-core.js", "r") as f:
            self.js_context = execjs.compile(f.read())
        self.proxy = self.update_proxy()
        self.ocr_client = AipOcr(
            self._BAIDU_APP_ID, self._BAIDU_API_KEY, self._BAIDU_SECRET_KEY)

        self.session = requests.session()
        self.session.mount("http://", HTTPAdapter(max_retries=3))

    def update_proxy(self):
        r = requests.get("http://127.0.0.1:5010/get/")
        if r.status_code == 200:
            result = r.json()
            print(result)
            p = "http://" + result["proxy"]
            print("代理: " + p)
            return p
        return None

    def searchOrderAppointmentSettings(self):
        try:
            r = self.session.post(
                self.order_url + "searchOrderAppointmentSettings.action", proxies={"http": self.proxy}, timeout=15)
            if r.status_code == 200:
                result = r.json()
                print("基础信息: {}".format(result))

                if result["result"]["success"]:
                    self.appointmentSettings = result["result"]["extend"]["appointmentSettings"]
                else:
                    print(result['result']["msg"])

            else:
                print("获取失败: ", r.status_code)
                self.update_proxy()
        except Exception as e:
            print(e)
            self.update_proxy()

    def makeToken(self):
        if len(self.appointmentSettings) > 0:
            appointmentSetting = self.appointmentSettings[0]
            if appointmentSetting:
                key = appointmentSetting['deliverTimeApart'] + \
                    str(appointmentSetting['remainApoointmentPersonCountApart'])
                message = appointmentSetting['deliverTimeDepart'] + str(
                    appointmentSetting['remainApoointmentPersonCountDepart'])

                print("key = ", key)
                print("message = ", message)

                return self._encryptByDES(key, message)
        return None

    def _encryptByDES(self, key, message):
        return self.js_context.call("encryptByDES", key, message)

    def image_code(self):
        try:
            url = self.order_url + "creatImgCode.action?d=" + \
                str(round(time.time() * 1000))
            print("图片地址:", url)

            r = self.session.get(url, proxies={"http": self.proxy}, timeout=10)
            if (r.status_code == 200):
                image_path = "image_code.jpg"
                with open(image_path, "wb+") as f:
                    f.write(r.content)
                image = Image.open(image_path)
                image.show()

                # ie = ImageEnhance.Contrast(image)
                # image = ie.enhance(2)

                # br = ImageEnhance.Brightness(image)
                # image = br.enhance(2)

                # co = ImageEnhance.Color(image)
                # image = co.enhance(10);

                # sh = ImageEnhance.Sharpness(image)
                # image = sh.enhance(2)

                # image = image.convert("L")

                # text = pytesseract.image_to_string(image)
                # image.show()

                options = {}
                options["language_type"] = "ENG"
                options["detect_direction"] = True
                options["detect_language"] = False
                options["probability"] = False

                result = self.ocr_client.basicAccurate(r.content, options)

                words_result_num = result["words_result_num"]
                if words_result_num > 0:
                    words_result = result["words_result"]
                    if len(words_result) > 0:
                        self.validate_code = str(
                            words_result[0]["words"]).strip()
                        print("验证码:" + self.validate_code)
                # text = self.OCR_lmj(image_path)
                print(result)
            else:
                print("获取验证码失败")
        except Exception as e:
            print(e)

    def commit_form(self, name="", card="", airport="", last4_number="", start="", end="", phone="", time="", buy_count=0):
        if None == self.token or None == self.validate_code:
            print("预约失败， token 或者验证码无效！")
            return
        self.start_station = start
        self.end_station = end

        parameter = {
            "userName": name,
            "idCard": card,
            "airways": airport,
            "flightNo": last4_number,
            "startStation": start,
            "terminalStation": end,
            "flightDate": time,
            "telNumber": phone,
            "appointCount": buy_count,
            "validateCode": self.validate_code,
            "token": self.token
        }

        try:
            r = self.session.post(
                self.order_url + "appointment.action", proxies={"http": self.proxy}, data=parameter, timeout=15)
            if r.status_code == 200:
                result = r.json()
                print(result)
                return result
            else:
                print("预定单提交失败")
        except Exception as e:
            print(e)
            print("预约失败， 出现代码错误")
        return None

    # 检测是否可以进行预约
    def check_can_order(self):
        if self.appointmentSettings and len(self.appointmentSettings) > 0:
            appointmentSetting = self.appointmentSettings[0]

            remainApoointmentPersonCountApart = appointmentSetting[
                "remainApoointmentPersonCountApart"]
            remainApoointmentPersonCountDepart = appointmentSetting[
                "remainApoointmentPersonCountDepart"]

            if remainApoointmentPersonCountDepart > 1 and remainApoointmentPersonCountApart > 1:
                return True

        return True

    # 显示收获地址
    def show_deliver_info(self):
        sj, dz_f, dz_t = "", "", ""
        if len(self.appointmentSettings) > 0:
            appointmentSetting = self.appointmentSettings[0]
            if appointmentSetting:
                if self.start_station == '贵阳':
                    sj = appointmentSetting['deliverTimeDepart']
                    dz_f = appointmentSetting['deliveryPlaceDepart']
                    dz_t = appointmentSetting['deliveryPlaceDepartDescription']
                elif self.end_station == '贵阳':
                    sj = appointmentSetting['deliverTimeApart']
                    dz_f = appointmentSetting['deliveryPlaceApart']
                    dz_t = appointmentSetting['deliveryPlaceApartDescription']

        return '提货时间：' + sj + '                   提货地址：' + dz_f + '' + dz_t


def do_order(name="", card="", airport="", last4_number="", start="", end="", phone="", time="", buy_count=0):
    gz = gzairports()
    gz.searchOrderAppointmentSettings()
    if gz.check_can_order():
        gz.makeToken()
        gz.image_code()
        result = gz.commit_form(
            name, card, airport, last4_number, start, end, phone, time, buy_count)

        if result and result["result"]["success"] == True:
            return gz

    return None


if __name__ == "__main__":
    gz = gzairports()
    print("检测是否可以预定")
    loop_count = 0
    while True:
        if loop_count > 10:
            gz.update_proxy()
            loop_count = 0
        # 获取数据
        gz.searchOrderAppointmentSettings()
        if gz.check_can_order():
            break
        loop_count += 1

    with ThreadPoolExecutor(max_workers=5) as pool:
        mission_list = []

        for i in range(10):
            mission_list.append(pool.submit(do_order, "郎岩", "23540719510611274566",
                                            "南方", "1234", "贵阳", "洛阳", "13199123089", "2019-11-07", 1))

        print("已开启100个线程，进行预定")
        for mission in as_completed(mission_list):
            gz = mission.result()
            if gz:
                print(gz.show_deliver_info())
                break

        print("预定任务全部结束!")

    # gz.validate_code = input("请输入验证码")

    # loop_count = 0
    # while True:
    #     try:
    #         result = gz.commit_form("郎岩", "23540719510611274566", "南方", "1234", "贵阳", "洛阳", "13199123089", "2019-11-07", 1)
    #         if result and result["result"]['success'] == True:
    #             print("预约成功");
    #             break;
    #         else:
    #             if (loop_count > 10):
    #                 gz.update_proxy()
    #                 loop_count = 0
    #             print("当前时间: {}".format(time.ctime()))
    #     except Exception as e:
    #         print(e)
    #         gz.update_proxy()

    #     loop_count += 1
