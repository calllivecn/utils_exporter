

from miio import (
    Device,
    exceptions,
) 
# from miio.chuangmi_plug import ChuangmiPlug

# 小米米家智能插座WIFI版
class MiPlug3_WIFI(Device):

    def set(self, SIID, PIID, VALUE):
        return self.send(
            "set_properties",
            [{'did': f'set-{SIID}-{PIID}', 'piid': PIID, 'siid': SIID, 'value': VALUE}]
        )

    def get(self, SIID, PIID):
        return self.send(
            "get_properties",
            [{'did': f'set-{SIID}-{PIID}', 'piid': PIID, 'siid': SIID}]
        )

    def on(self): # 打开开关
        return self.set(2, 1, True)

    def off(self): # 关闭开关
        return self.set(2, 1, False)
    
    def switch_status(self) -> bool:
        data = self.get(2, 1)
        return data[0]["value"]


    def temperature(self):
        data = self.get(2, 2)
        if data:
            return data[0]["value"]
    


# 米家智能插座3
class MiPlug3(Device):
    def set(self, SIID, PIID, VALUE):
        return self.send(
            "set_properties",
            [{'did': f'set-{SIID}-{PIID}', 'piid': PIID, 'siid': SIID, 'value': VALUE}]
        )

    def get(self, SIID, PIID):
        return self.send(
            "get_properties",
            [{'did': f'set-{SIID}-{PIID}', 'piid': PIID, 'siid': SIID}]
        )
    

    def switch_status(self) -> bool:
        data = self.get(2, 1)
        return data[0]["value"]

    def on(self): # 打开开关
        return self.set(2, 1, True)

    def off(self): # 关闭开关
        return self.set(2, 1, False)

    def lock(self): # 启用物理锁
        return self.set(7, 1, True)

    def unlock(self): # 解除物理锁
        return self.set(7, 1, False)

    def temperature(self): # 温度
        data = self.get(12, 2)
        if data:
            return data[0]['value']

    def power_consumption(self):
        # 能量消耗
        data = self.get(11, 1)
        if data:
            return data[0]["value"]

    def electric(self): # 功率
        data = self.get(11, 2)
        if data:
            return data[0]['value']


def test():
    import os
    import time

    IP = os.environ["MIROBO_IP"]
    TOKEN = os.environ["MIROBO_TOKEN"]

    dev = MiPlug3(ip=IP, token=TOKEN)

    while True:
        try:
            watt = dev.electric()
            temp = dev.temperature()

            E = dev.power_consumption()

            switch = dev.switch_status()

            print(f"开关状态：{switch}")
            print(f"当前功率：{watt} w")
            print(f"当前温度：{temp} ℃")
            print(f"已使用能量：{E} kWh ?")

        except exceptions.DeviceException as e:
            print(f"异常... {e}")

        time.sleep(5)


if __name__ == "__main__":
    test()
