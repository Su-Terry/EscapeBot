FROM python:3

RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY requirements.txt /bot/
RUN pip install -r requirements.txt

COPY . /bot

CMD [ "python3", "bot.py" ]
