

import sys
import time
import json
import asyncio
import traceback
import argparse
import dataclasses
from pathlib import Path
from urllib import request

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


import httpx


from prometheus_client import (
    Gauge,
    Info,
    start_http_server,
)


CFG="""\
[exporter_conf]
address="::"
port=19100
# 指标更新间隔 单位 秒
interval=30

# 配置代理
#proxy="http://user:pass@host:port"
#proxy="socks5://user:pass@host:port"


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

    while True:
        try:
            data = request.urlopen(req, timeout=30)
        except Exception as e:
            traceback.print_exception(e)

            time.sleep(30)
            continue

        break

    context = data.read()
    return json.loads(context)


class AsyncGet:
    def __init__(self, proxy: str = None):

        self._aclient = httpx.AsyncClient(http2=True, proxy=proxy)


    async def get(self, url, headers={"User-Agent": "curl/7.81.0"}):

        result = await self._aclient.get(url, headers=headers)
        return result.json()
    

    async def aclose(self):
        await self._aclient.aclose()


@dataclasses.dataclass
class NameURL:
    name: str
    url: str


class JMS:

    labels=["name"]

    def __init__(self, nameurl: list[NameURL], proxy: str):
        self._list_name_url = nameurl
        
        self.total = Gauge("jms_total_bytes", "总共量", self.labels)
        self.usage = Gauge("jms_usage_bytes", "已使用量", self.labels)
        self.reset_day = Gauge("jms_reset_day", "jms 套餐信息, 每月重置日。", self.labels)

        # 之后想要使用asyncio
        self._a_get = AsyncGet(proxy)
    

    def update_all(self):
        for jms in self._list_name_url:
            self.__update(jms)
    

    async def a_update_all(self, sleep_: float):

        while True:

            tasks = (self.__a_update(jms) for jms in self._list_name_url)

            try:
                await asyncio.gather(*tasks)
            except BaseException as e:
                traceback.print_exception(e)

            await asyncio.sleep(sleep_)

    
    def __update(self, nameurl: NameURL):
        
        result = get(nameurl.url)

        total = result["monthly_bw_limit_b"]
        usage = result["bw_counter_b"]
        reset_day = result["bw_reset_day_of_month"] 


        self.total.labels(name=nameurl.name).set(total)
        self.usage.labels(name=nameurl.name).set(usage)
        self.reset_day.labels(name=nameurl.name).set(reset_day)
    

    async def __a_update(self, nameurl: NameURL):

        result = await self._a_get.get(nameurl.url)

        total = result["monthly_bw_limit_b"]
        usage = result["bw_counter_b"]
        reset_day = result["bw_reset_day_of_month"] 


        self.total.labels(name=nameurl.name).set(total)
        self.usage.labels(name=nameurl.name).set(usage)
        self.reset_day.labels(name=nameurl.name).set(reset_day)
        



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

    update_interval = conf["exporter_conf"].get("interval")

    # 生成实例
    jmss = []
    for jms in conf.get("jms"):
        jmss.append(NameURL(name=jms["name"], url=jms["url"]))
    
    proxy = conf["exporter_conf"].get("proxy")
    
    # 生成
    jms = JMS(jmss, proxy)

    # 启动iexporter server
    wsgi, thread = start_http_server(port=server_port, addr=server_addr)


    """
    while True:
        # jms实例
        jms.update_all()
        time.sleep(update_interval)
    """

    asyncio.run(jms.a_update_all(update_interval))

    jms._a_get.aclose()


if __name__ == "__main__":
    main()
