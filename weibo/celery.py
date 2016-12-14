from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('weibo',
            broker='amqp://',
            backend='amqp://',
            include=['weibo.tasks'])

if __name__ == '__main__':
    app.start()