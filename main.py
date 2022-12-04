from datetime import datetime
from session import Session
import os
import json

ENV_KEYS = ['DATA']

info_str = os.environ['DATA']
info = json.loads(info_str)
username = info.pop('studentid')
password = info.pop('password')

if __name__ == '__main__':
    print(datetime.now())
    s = Session()
    s.login(username, password)

    if s.request_passed(info['delta']):
        exit(0)

    try:
        s.save_request(**info)

    except Exception as e:
        msg = e.args[0]['msg'] if 'msg' in e.args[0] else e.args[0]
        if '存在尚未审核通过的园区往返申请记录' in msg or '不能再次申请' in msg:
            s.get_latest()
        else:
            print(msg)
            exit(1)

    s.submit()
    print('已申请')
