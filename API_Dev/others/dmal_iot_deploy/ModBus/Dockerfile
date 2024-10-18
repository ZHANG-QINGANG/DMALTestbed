FROM python:3.9
WORKDIR /Web
COPY ./Web/requirements.txt ./
RUN pip install -r requirements.txt
#RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple some-package

#COPY ./website	/website
#ENV LISTEN_PORT 9090
#EXPOSE 9090
#ENV LISTEN_PORT 5000
#EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD ["-u", "gevent_server.py"]
