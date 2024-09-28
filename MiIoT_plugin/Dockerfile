FROM alpine-py3:latest as BUILDER

COPY app/ /app/
COPY README.md requireument.txt /app/

RUN python -m venv /app/.venv \
&& apk add python3-dev gcc musl-dev linux-headers

RUN source /app/.venv/bin/activate \
&& pip install -r /app/requireument.txt

#RUN pip install --break-system-packages -r requireument.txt


FROM alpine-py3:latest

COPY --from=BUILDER /app/ /app/

ENV PATH=/app/.venv/bin:$PATH

WORKDIR /app

CMD ["python", "mi-plugin.py"]

EXPOSE 19101

