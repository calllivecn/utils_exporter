# JMS 流量监控


## 使用方式一：使用python虚拟环境

- 略


## 使用方式二：容器使用

- 编写配置文件

```toml
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


# 这是配置第二个实例, 如果有。
#[[jms]]
#url=
#name="jms2"

```

- 构建镜像

```shell
podman/docker build -t jms\_exporter:latest .
```


- 运行

```shell
podman/docker run -d --name jms -v <jms.toml>:/jms.toml -p 19100:19100 jms:latest
```

