from logging import DEBUG, debug
import os
from typing import Iterable
import smtplib

from flask import Flask, json, request
from flask_httpauth import HTTPBasicAuth

class EnvironmentVariableNotFound(EnvironmentError):
    pass

def check_required_env_variables(*args):
    for var in args:
        if os.environ.get(var) is None:
            raise EnvironmentVariableNotFound(var)

check_required_env_variables(
    'AUTH_USERNAME', 'AUTH_PASSWORD',
    'SMTP_HOST', 'SMTP_PORT',
    'SMTP_USERNAME', 'SMTP_PASSWORD', 'TO_EMAIL')

mail_msg = """\
Subject: NotificationService %s

%s"""

app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify(username, password):
    if username == os.environ.get('AUTH_USERNAME') and\
       password == os.environ.get('AUTH_PASSWORD'):
       return username


@app.route('/', methods=['POST'])
@auth.login_required
def push_notification():
    data = request.json


    with smtplib.SMTP_SSL(os.environ.get('SMTP_HOST'), os.environ.get('SMTP_PORT')) as server:
        server.login(os.environ.get('SMTP_USERNAME'), os.environ.get('SMTP_PASSWORD'))
        server.sendmail(from_addr=os.environ.get('SMTP_USERNAME'),
                        to_addrs =os.environ.get('TO_EMAIL'),
                        msg= mail_msg % (data['subject'], data['content']))

    return "Ok"



if __name__ == '__main__':
    app.run(port=8080, debug=True)