

import sys
import time
import argparse
import dataclasses
from pathlib import Path

from typing import (
    List,
    Dict,
)

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib



from prometheus_client import (
    Gauge,
    Info,
    start_http_server,
)


from miio_device import (
    MiPlug3_WIFI,
    MiPlug3,
    Device,
    exceptions,
)


CFG="""\
[exporter_conf]
address="0.0.0.0"
port=19100
# 指标更新间隔 单位 秒
interval=10

# 这是配置第一个实例
[[MiPlugins]]

# 在prometheus 中 name 标签的值
name="小米智能插座3"

# value choice: ["MiPlug3_WIFI", "MiPlug3"]
type=

ip=
token=


# 这是配置第二个实例
#[[MiPlugins]]
#name="简单插座"
#type=
#ip=
#token=

"""

def readcfg(filepath: Path):

    if filepath.is_file():
        with open(filepath, "rb") as f:
            return tomllib.load(f)
    else:
        with open(filepath, "w") as f:
            f.write(CFG)

        raise ValueError(f"可能是首次运行需要修改文件: {str(filepath)}")


@dataclasses.dataclass
class Plugincfg:
    name: str
    ip: str
    token: str
    mi_device: Device


class MiDevice:

    labels=["name", "ip"]

    def __init__(self, pluginlist: List[Plugincfg]):
        self._list_pluginlist = pluginlist
        
        # exporter info
        self.info = Info('build_version', 'Description of info')
        self.info.info({'version': '0.1'})


        self.alive = Gauge('IoT_Mi_plugin_alive', '设备是否在线 value: [0, 1]', self.labels)
        self.power = Gauge('IoT_Mi_plugin_staus', '插座的开头状态 value: bool', self.labels)

        # 插座温度
        self.temp = Gauge('IoT_Mi_plugin_temperature', '设备温度', self.labels)

        # 当前功率
        self.watt = Gauge('IoT_Mi_plugin_watt', '插座功率', self.labels)

    

    def update_all(self):
        for plu in self._list_pluginlist:
            try:
                self.__update(plu)
            except exceptions.DeviceException as e:
                print(f"请求异常: {plu}")

    
    def __update(self, plu: Plugincfg):

        alive_bool = plu.mi_device.switch_status()
        
        if alive_bool:
            alive = 1 
            power = 1
            temp = plu.mi_device.temperature()

            if hasattr(plu.mi_device, "electric"):
                watt = plu.mi_device.electric()
            else:
                watt = -1

        else:

            alive = 0
            power = 0
            temp = -99
            watt = -1


        self.alive.labels(name=plu.name, ip=plu.ip).set(alive)
        self.power.labels(name=plu.name, ip=plu.ip).set(power)
        self.temp.labels(name=plu.name, ip=plu.ip).set(temp)
        self.watt.labels(name=plu.name, ip=plu.ip).set(watt)




def main():
    parse = argparse.ArgumentParser(usage="%(prog)s [-c <conf.toml>]")

    parse.add_argument("-c", "--conf", action="store", type=Path, default=Path("mi-plugin.toml"), help="指定配置文件")
    parse.add_argument("--parse", action="store_true", help=argparse.SUPPRESS)


    args = parse.parse_args()

    if args.parse:
        parse.print_help()
        sys.exit(0)

    
    # 加载配置文件
    conf = readcfg(args.conf)

    server_addr = conf["exporter_conf"].get("address")
    server_port = conf["exporter_conf"].get("port")

    update_interval = conf["exporter_conf"].get("interval")

    plugins = []
    for plu in conf.get("MiPlugins"):
        if plu["type"] == "MiPlug3_WIFI":
            dev = MiPlug3_WIFI(ip=plu["ip"], token=plu["token"])
            plugins.append(Plugincfg(name=plu["name"], ip=plu["ip"], token=plu["token"], mi_device=dev))

        elif plu["type"] == "MiPlug3":
            dev = MiPlug3(ip=plu["ip"], token=plu["token"])
            plugins.append(Plugincfg(name=plu["name"], ip=plu["ip"], token=plu["token"], mi_device=dev))
        
        else:
            raise TypeError("""不支持的类型[[MiPlugins]]: type: ["MiPlug3_WIFI", "MiPlug3"]""")

    
    # 生成
    mi_devs = MiDevice(plugins)

    # 启动iexporter server
    start_http_server(port=server_port, addr=server_addr)

    while True:
        # jms实例
        mi_devs.update_all()
        time.sleep(update_interval)


if __name__ == "__main__":
    main()