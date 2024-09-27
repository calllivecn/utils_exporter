FROM alpine-py3:latest

COPY jms.py README.md ../requireument.txt /

RUN pip install --break-system-packages -r requireument.txt

EXPOSE 19100

CMD ["python", "/jms.py"]

