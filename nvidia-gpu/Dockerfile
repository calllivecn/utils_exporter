FROM ubuntu:22.04 as BUILDER

RUN apt update \
&& apt -y install python3 python3-pip

COPY app/ /app/

COPY README.md requireument.txt /app/

workdir /app/

RUN pip install -U --break-system-packages pip || pip install -U pip \
&& pip install --break-system-packages -r requireument.txt \
&& pyinstaller nvidia-smi-exporter.spec


RUN echo "使用类似以下命令拿到可执行二进制文件" \
&& echo "podman/docker cp <images_name:tag_name>:/build ."

