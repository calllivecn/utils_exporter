

import sys
import time
import json
import argparse
from pathlib import Path
from urllib import request

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


CFG="""\
[exporter_conf]
address="0.0.0.0"
port=19100
# 指标更新间隔 单位 秒
interval=30

# 这是配置第一个实例
[[jms]]
# https://justmysocks6.net/members/getbwcounter.php?service=xxxxx&id=xxxxx-xxxxxxx-xxxxxxx-xxxxxxxxxx
url=
# 给实例起个名字
name="jms1"


# 这是配置第二个实例
#[[jms]]
#url=
#name="jms2"

"""

def readcfg(filepath: Path):

    if filepath.is_file():
        with open(filepath, "rb") as f:
            return tomllib.load(f)
    else:
        with open(filepath, "w") as f:
            f.write(CFG)

        raise ValueError(f"可能是首次运行需要修改文件: {str(filepath)}")



def get(url, headers={"User-Agent": "curl/7.81.0"}):
    """
    param url: jms counter api URL.
    return: {'monthly_bw_limit_b': 500000000000, 'bw_counter_b': 75678957390, 'bw_reset_day_of_month': 13}
    """
    req = request.Request(url, headers=headers, method="GET")
    data = request.urlopen(req, timeout=30)
    context = data.read()
    return json.loads(context)



class JMS:

    labels=["name"]

    def __init__(self, name, url):
        self.name = name
        self.url = url
        
        self.total = Gauge("jms_total_bytes", "总共量", self.labels)
        self.usage = Gauge("jms_usage_bytes", "已使用量", self.labels)
        self.reset_day = Gauge("jms_reset_day", "jms 套餐信息, 每月重置日。", self.labels)

    
    def update(self):
        result = get(self.url)

        total = result["monthly_bw_limit_b"]
        usage = result["bw_counter_b"]
        reset_day = result["bw_reset_day_of_month"] 


        self.total.labels(name=self.name).set(total)
        self.usage.labels(name=self.name).set(usage)
        self.reset_day.labels(name=self.name).set(reset_day)



def main():
    parse = argparse.ArgumentParser(usage="%(prog)s [-c <conf.toml>]")

    parse.add_argument("-c", "--conf", action="store", type=Path, default=Path("jms.toml"), help="指定配置文件")
    parse.add_argument("--parse", action="store_true", help=argparse.SUPPRESS)


    args = parse.parse_args()

    if args.parse:
        parse.print_help()
        sys.exit(0)

    
    # 加载配置文件
    conf = readcfg(args.conf)

    server_addr = conf["exporter_conf"].get("address")
    server_port = conf["exporter_conf"].get("port")

    update_interval = float(conf["exporter_conf"].get("interval"))

    # 生成实例
    JMSS = []
    for jms in conf.get("jms"):
        JMSS.append(JMS(jms["name"], jms["url"]))


    # 启动iexporter server
    start_http_server(port=server_port, addr=server_addr)

    while True:
        # jms实例
        for jms in JMSS:
            jms.update()
        
        time.sleep(update_interval)


if __name__ == "__main__":
    main()