

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib



from prometheus_client import (
    Gauge,
    Info,
)


# 设备信息
i = Info('my_build_version', 'Description of info')
i.info({'version': '0.1', 'buildhost': 'foo@bar'})


Mi_lables = ["instance", "name"]

alive = Gauge('IoT_Mi_plugin_alive', '设备是否在线', Mi_lables)
status = Gauge('IoT_Mi_plugin_staus', '插座的开头状态', Mi_lables)
# 插座温度
temp = Gauge('IoT_Mi_plugin_temperature', '设备温度', Mi_lables)

# 当前功率
watt = Gauge('IoT_Mi_plugin_watt', '插座功率', Mi_lables)


watt.labels({"instance": "jms", "name": "zx jms"}).set(w)


def main():
    pass