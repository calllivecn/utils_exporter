
from miio import Device
from miio.chuangmi_plug import ChuangmiPlug


class MiPlug(Device):
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

    def lock(self): # 启用物理锁
        return self.set(7, 1, True)

    def unlock(self): # 解除物理锁
        return self.set(7, 1, False)

    def electric(self): # 功率
        data = self.get(11, 2)
        if data:
            return data[0]['value']

    def temperature(self): # 温度
        data = self.get(12, 2)
        if data:
            return data[0]['value']


# d = ChuangmiPlug(ip=IP, token=TOKEN)
