# Mi IoT 插座


## 使用方式一：使用python虚拟环境

- 略

## 使用方式二：容器使用

- 编写配置文件

```toml
[exporter_conf]
address="::"
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
```


- 构建镜像

```shell
podman/docker build -t miiot:latest .
```


- 运行

```shell
podman/docker run -d --name miiot -v <mi-plugin.toml>:/app/mi-plugin.toml -p 19101:19101 miiot:latest
```

