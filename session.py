import random
import logging
from functools import wraps
from string import ascii_letters, digits
from datetime import datetime, timedelta
from requests import Session
from urllib import parse
from requests_toolbelt import MultipartEncoder

from const import URL
from tools import prettify, format_date


class Session(Session):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'TE': 'Trailers',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
        })

    def __del__(self):
        self.close()

    def get(self, url, *args, **kwargs):
        """重写 get 方法，验证状态码，转化为 json"""
        res = super().get(url, *args, **kwargs)
        res.raise_for_status()
        return res

    def post(self, url, *args, **kwargs):
        """重写 post 方法，验证状态码，转化为 json"""
        res = super().post(url, *args, **kwargs)
        res.raise_for_status()

        return res

    def login(self, username: str, password: str) -> bool:
        """登录门户，重定向出入校申请"""
        # IAAA 登录
        json = self.post(URL.OAUTHLOGIN, data={
            "userName": username,
            "appid": "portal2017",
            "password": password,
            "redirUrl": URL.LOGIN_REDIRECT,
            "randCode": "",
            "smsCode": "",
            "optCode": "",
        }).json()
        assert json['success'], json

        # 门户 token 验证
        self.get(URL.SSO_LOGIN, params={
            '_rand': random.random(),
            'token': json['token']
        })

        # 学生出入校重定向
        res = self.get(URL.STUDENT_EXEN_APP)
        redir = parse.parse_qs(parse.urlparse(res.url).query)
        token = redir['token'][0]

        # 登录学生出入校
        json = self.get(URL.SIMSO_LOGIN, params={
            'token': token
        }).json()
        assert json['success'], json
        sid = json['sid']

        # 设置请求参数
        self.params['sid'] = sid
        self.params['_sk'] = username
        self.cookies.set('sid', sid, domain='simso.pku.edu.cn')

        # 获取出入校申请时段信息
        return self.login_check()

    def login_check(self):
        """检查是否已登录"""
        json = self.get(URL.LOGIN_CHECK).json()
        return json['success'] and json['row']['sfyxsq'] == 'y'

    @wraps('check_login')
    def login_check_wrapper(func):
        def wrapper(self, *args, **kwargs):
            if not self.login_check():
                raise Exception('You should login first to use this method')
            return func(self, *args, **kwargs)
        return wrapper

    @login_check_wrapper
    def status(self):
        """获取申请状态（当前是否可申请）"""
        json = self.get(URL.REQUEST_STATUS).json()
        assert json['success']
        return json

    def get_supplement(self):
        """获取补充信息"""
        lxxx = self.status()['row']['lxxx']
        lxxx.update(dzyx=lxxx['email'], lxdh=lxxx['yddh'])
        assert all(k in lxxx for k in [
                   'yddh', 'ssfjh', 'ssl', 'ssyq', 'dzyx', 'lxdh']), '无法获取住宿、联系信息'
        return lxxx

    def save_request(self, exen_type='园区往返', start='', end='', track='', places=[], description='', delta=0, **supplements):
        """尝试保存出入校信息
        `exen_type`: 出入校类型
        `track`: 出入校出行轨迹
        `description`: 出入校具体事项
        `places`: 园区往返地点
        `start`: 出入校起点（出入校申请）
        `end`: 出入校终点（出入校申请）
        `delta`: 申请时间（今天 or 明天）
        `supplements`: 补充信息如: qdxm, zdxm

        出入校申请填写: `exen_type`, `start`, `end`, `track`, `description`
        园区往返填写: `places`, `description`
        """
        template = {
            # 公有信息
            "crxrq": format_date(delta),  # 出入校日期
            "crxsy": exen_type,          # 出入校事由(园区往返 或 出入校申请中的具体事由)
            'crxjtsx': description,        # 出入校具体事项

            # 出入校申请
            "crxqd": start,  # 出入校起点
            "crxzd": end,   # 出入校终点
            "crxxdgj": track,  # 出入校行动轨迹
            "qdxm": "",    # 起点校门
            "zdxm": "",    # 终点校门

            # 园区往返
            'yqc': places,  # 园区出
            'yqr': places,  # 园区入

            # 提交/审核
            "sqbh": "",  # 申请编号
            "tjbz": "",  # 提交标志（是否点击提交）
            "shbz": "",  # 审核标志（是否被审核）
            "shyj": "",  # 审核意见

            # 班车
            "qdbc": "",  # 起点班次
            "zdbc": "",  # 终点班次

            # 位置编码
            "gjdqm": "156",  # 国家地区码
            "ssdm": "11",  # 省市代码
            "djsm": "01",  # 地级市码
            "xjsm": "08",  # 县级市码
            "jd": "中关村",  # 街道

            # 返校相关
            "dfx14qrbz": "y",  # 返校 14 日内保证？
            "fxjwljs": "",  # 返校xxxx
            "fxzgfxljs": "",  # 返校xxxx
            "fxqzmj": "",  # 返校xxxx
            "fxyczz": "",  # 返校xxxx
            "djsjbz": "y",  # 抵京时间保证
            "djrq": "",  # 抵京日期

            # 未知
            "sfyxtycj": "",  # 是否允许???
            "bcsm": ""       # ???
        }
        template.update(**self.get_supplement())
        template.update(supplements)

        logging.debug(prettify(template))

        json = self.post(URL.SAVE_REQUEST, params={
                         'applyType': 'yqwf'}, json=template).json()
        assert json['success'], json

        self.sqbh = json['row']  # 申请编号
        return

    def upload_img(self, img, cldms):
        assert self.sqbh, '请先获取申请编号！'
        assert cldms in ['bjjkb', 'xcm'], '文件上传类型应当为 bjjkb / xcm'

        boundary = '------WebKitFormBoundary' + \
            ''.join(random.choices(ascii_letters + digits, k=16))

        fields = {
            'files': (f'WechatIMG{random.randint(50, 150)}.jpeg', img, 'image/jpeg'),
            'cldms': cldms,
            'sqbh': self.sqbh
        }

        m = MultipartEncoder(fields=fields, boundary=boundary)
        json = self.post(URL.UPLOAD_IMG, headers={
                         'Content-Type': m.content_type}, data=m).json()

        assert json['success'], json

    def fake_img(self):
        self.upload_img(b'empty image', 'xcm')
        self.upload_img(b'empty image', 'bjjkb')

    def submit(self) -> bool:
        assert self.sqbh, "请先获取申请编号！"
        json = self.get(URL.SUBMIT, params={'sqbh': self.sqbh}).json()
        assert json['success'], json

    def request_list(self) -> list[dict]:
        json = self.get(URL.QUERY_REQUEST).json()
        assert json['success']

        return json['row']

    def get_latest(self) -> dict:
        """获取最近的申请信息"""
        latest = self.request_list()[0]

        self.sqbh = latest['sqbh']
        return latest

    def request_passed(self, delta=1):
        """申请是否已通过"""
        date = (datetime.now() + timedelta(days=delta)).strftime('%Y%m%d')
        for row in self.request_list():
            if row.get('crxrq', -1) == date and row.get('shbz', -1) == '审核通过':
                print(f'{date} 申请已通过')
                return True
        else:
            print(f'{date} 申请未通过')
            return False
