# linux nvidia-gpu 状态监控

## 使用 容器+pyinstaller 打包成单一可执行文件

- 使用 `podman/docker build -t nvidia-smi-exporter .` 打包

- 然后 `podman/docker run -it --rm --name nvidia-smi-exporter bash`

- 导出 可执行文件 `podman/docker cp nvidia-smi-exporter:/app/dist/nvidia-smi-exporter .`

