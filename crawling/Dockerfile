FROM python:3.14-rc


COPY requirements.txt /user/
RUN pip install --no-cache-dir -r /user/requirements.txt
RUN pip install --upgrade pip
RUN useradd -ms /bin/bash user
USER user


WORKDIR /home/jbrauxxx/Documents/crawling
VOLUME ["/home/jbrauxxx/Documents/crawling"]
COPY requirements.txt /user/
RUN pip install --no-cache-dir -r /user/requirements.txt
RUN python3 -m pip install --upgrade pip 
EXPOSE 8000
#CMD [ "python3", "./aven.py" ]

