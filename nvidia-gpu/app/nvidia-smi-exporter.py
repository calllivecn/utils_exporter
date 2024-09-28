
from typing import (
    Any,
    List,
    Tuple,
)

import sys
import time
import copy
import traceback
import subprocess
from pathlib import Path
from collections import OrderedDict


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


    def get_metric(self) -> Tuple[List[Any], List[Any]]:

        labels_len = len(self.metric_labels)
        # gauges_len = len(self.metric_gauges)

        metrics = self.__exec(list(self.metric_labels.values()) + list(self.metric_gauges.values()))

        return metrics[:labels_len], metrics[labels_len:]


    def __exec(self, nvidia_querys: List[str]) -> List[Any]:

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

            for field in fields:
                l2.append(self.convert(field))


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

        self.gauges_obj = []
        for gauge in self.gauges.keys():
            self.gauges_obj.append(Gauge(gauge, gauge, labelnames=self.labels))


    def update_all(self):

        labels = copy.deepcopy(self.labels)
        gauges = copy.deepcopy(self.gauges)

        labels_v, gauges_v = self.smi.get_metric()

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
