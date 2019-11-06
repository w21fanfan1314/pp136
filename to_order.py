import requests
import binascii
import crypto.Cipher.DES
import crypto.Util.Padding




class gzairports():
    order_url = "http://www.gzairports.com:11111/"
    # 查询到预设参数
    appointmentSettings = list()
    # token
    token = ""


    def searchOrderAppointmentSettings(self):
        r = requests.post(self.order_url + "searchOrderAppointmentSettings.action")
        if r.status_code == 200:
            result = r.json()

            if result["result"]["success"]:
                self.appointmentSettings = result["result"]["extend"]["appointmentSettings"]
            else:
                print(result['result']["msg"])

        else:
            print("获取失败: ", r.status_code)

    def makeToken(self):
        appointmentSetting = self.appointmentSettings[0];
        if appointmentSetting:
            key = appointmentSetting['deliverTimeApart'] + appointmentSetting['remainApoointmentPersonCountApart'];
            message = appointmentSetting['deliverTimeDepart'] + appointmentSetting['remainApoointmentPersonCountDepart'];

            print("key = ", key)
            print("message = ", message)

            return self._encryptByDES(key, message)
        return None

    def _encryptByDES(key, message):
        key_hex = binascii.b2a_hex(key.encode("utf-8"))
        cipher = crypto.Cipher.DES.new(key=key_hex, mode= crypto.Cipher.DES.MODE_ECB)
        return cipher.encrypt(crypto.Util.Padding(message, style="Pkcs7"))


if __name__ == "__main__":
    gz = gzairports()
    gz.searchOrderAppointmentSettings()

    # print(gz.appointmentSettings)
    print(gz.makeToken())