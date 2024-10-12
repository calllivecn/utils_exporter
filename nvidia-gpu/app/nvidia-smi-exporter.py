
from typing import (
    Any,
)

import sys
import time
import copy
import traceback
import subprocess
from pathlib import Path
from collections import OrderedDict

from pprint import pprint


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


from prometheus_client import (
    Gauge,
    start_http_server,
)


def readcfg(filepath: Path):

    if filepath.is_file():
        with open(filepath, "rb") as f:
            return tomllib.load(f)
    
    else:
        raise FileNotFoundError(f"需要指定配置文件")


class NvidiaSMI:
    """
    使用 nvidia-smi 命令行工具拿数据
    """

    def __init__(self, metric_labels: OrderedDict, metric_gauges: OrderedDict, nvidia_smi_path: Path = Path("nvidia-smi"), timeout: float = 30.0):

        self.metric_labels = metric_labels
        self.metric_gauges = metric_gauges

        self.nvidia_smi_path = nvidia_smi_path
        self.timeout = timeout


    def get_metric(self) -> list[tuple[list[Any], list[Any]]]:

        labels_len = len(self.metric_labels)
        # gauges_len = len(self.metric_gauges)

        metrics = self.__exec(list(self.metric_labels.values()) + list(self.metric_gauges.values()))

        # multi gpu
        multi_gpu = []
        for gpu in metrics:
            multi_gpu.append((gpu[:labels_len], gpu[labels_len:]))

        print("multi_gpu:")
        pprint(multi_gpu)
        return multi_gpu


    def __exec(self, nvidia_querys: list[str]) -> list[list[Any]]:

        query_args = ",".join(nvidia_querys)

        cmd = [self.nvidia_smi_path, "--format=csv,noheader,nounits", f"--query-gpu={query_args}"]

        try:
            p = subprocess.run(cmd, capture_output=True, check=True, timeout=self.timeout)
        except Exception as e:
            traceback.print_exception(e)
            return

        l1 = p.stdout.decode().split("\n")

        # print(f"{l1=}")

        l2 = []
        for line in l1:

            if line == "":
                continue

            fields = line.split(", ")

            # print(f"{fields=}", end="")
            multi_gpu = []
            for field in fields:
                multi_gpu.append(self.convert(field))

            l2.append(multi_gpu)

        # print(f"{l2=}")

        return l2


    def convert(self, field: str):
        """
        把数值数的转换为数值
        """

        try:
            r = int(field)
        except ValueError:

            try:
                r = float(field)
            except ValueError:
                r = field
    
        return r


class Executer:

    def __init__(self, labels: OrderedDict, gauges: OrderedDict):

        self.smi = NvidiaSMI(labels, gauges)

        self.labels = labels
        self.gauges = gauges


        multi_gpu = self.smi.get_metric()
        for labels_v, gauges_v in multi_gpu:

            # 处理标签名：正则表达式 [a-zA-Z_][a-zA-Z0-9_]*
            # labels_v = [field.replect(" -", "_") for field in labels_v]
            

            self.gauges_obj = []
            for gauge in self.gauges.keys():
                self.gauges_obj.append(Gauge(gauge, gauge, labelnames=labels))

            # 创建Gauge 时，只需要一次/
            break
        


    def update_all(self):

        multi_gpu = self.smi.get_metric()

        for index, (labels_v, gauges_v) in enumerate(multi_gpu):

            labels = copy.deepcopy(self.labels)
            gauges = copy.deepcopy(self.gauges)

            for i, label in enumerate(labels.keys()):
                labels[label] = labels_v[i]

            for i, gauge in enumerate(self.gauges_obj):
                gauge.labels(**labels).set(gauges_v[i])

    


def main():
    
    # 加载配置文件
    try:
        conf = readcfg(Path(sys.argv[1]))
    except Exception as e:
        traceback.print_exception(e)

        print(f"Usage: {sys.argv[0]} <*.toml>")

        sys.exit(1)


    server_addr = conf["exporter_conf"].get("address")
    server_port = conf["exporter_conf"].get("port")
    update_interval = conf["exporter_conf"].get("interval")


    executer = Executer(OrderedDict(conf["metric_labels"]), OrderedDict(conf["metric_gauges"]))

    # 启动iexporter server
    wsgi, thread = start_http_server(port=server_port, addr=server_addr)

    while True:
        # jms实例
        executer.update_all()
        time.sleep(update_interval)


if __name__ == "__main__":
    main()
