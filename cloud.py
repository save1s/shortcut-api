import os
import time
import leancloud
from enum import Enum
from datetime import datetime
from utils import qzone_login
from utils import qzone


engine = leancloud.Engine()

RunRecord = leancloud.Object.extend('RunRecord')
Config = leancloud.Object.extend('Config')

today = datetime.today().strftime('%Y-%m-%d')  # '2019-03-27'

QQ_NUMBER = os.environ['LEANCLOUD_QQ_NUMBER']
QQ_PASSWORD = os.environ['LEANCLOUD_QQ_PASSWORD']
TARGET_QQ = os.environ.get('LEANCLOUD_TARGET_QQ', 2563280140)


class RunStatusEnum(Enum):
    UNKNOWN = 0
    RUN = 1
    NOT_RUN = 2


def save_run_status(date, run_status):
    """
    :param date: 日期字符串, 格式为: "2019-01-01"
    :param run_status: int 见 RunStatusEnum
    :return:
    """
    query = RunRecord.query
    query.equal_to('date', date)
    run_records = query.find()
    if run_records:
        run_record = run_records[0]
    else:
        run_record = RunRecord()
        run_record.set('date', date)
    run_record.set('status', run_status)
    run_record.save()


def get_run_status(date):
    """
    :param date: 日期字符串, 格式为: "2019-01-01"
    """
    query = RunRecord.query
    query.equal_to('date', date)
    run_records = query.find()
    if run_records:
        run_record = run_records[0]
        return run_record.get('status')
    else:
        return RunStatusEnum.UNKNOWN.value


def save_qq_cookies(cookies):
    """
    :param cookies: dict
    :return:
    """
    query = Config.query
    query.equal_to('key', 'qq_cookies')
    config = query.first()
    config.set('value', cookies)
    config.save()


def fetch_qq_cookies():
    query = Config.query
    query.equal_to('key', 'qq_cookies')
    config = query.first()
    return config.get('value')


@engine.define
def init_qq_cookies():
    cookies = {}
    cookies = qzone_login.login(QQ_NUMBER, QQ_PASSWORD)
    if not cookies.get('p_skey'):
        leancloud.logger.critical('获取cookie失败')
    save_qq_cookies(cookies)


@engine.define
def check_run():
    cookies = fetch_qq_cookies()
    q = qzone.Qzone(**cookies)
    shuoshuo = q.emotion_list(TARGET_QQ, num=1)
    result = run(shuoshuo[0].url)
    save_run_status(today, result)


@engine.define
def test_object_store():
    date = datetime.now().strftime('%Y-%m-%d')
    res_type = type(get_qq_cookies(date))
    cookies = {"now": datetime.now().strftime(
        '%Y年%m月%d日 %H时%M分'), 'type': str(res_type)}
    save_qq_cookies(cookies=cookies, date=date)


def run(url):
    """
    判断url的图片， 是跑还是不跑
    :param url:
    :return: 跑：1, 不跑 2, 不知道: 0
    """
    WHITE = 255
    BLACK = 0
    pic = qzone.Picture(url)
    image = Image.open(pic.open()).resize((100, 100)).convert('L')
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            pixels[x, y] = BLACK if pixels[x, y] < 20 else WHITE

    valid_picture_feature_points = []
    for x in range(image.width):
        valid_picture_feature_points.append(pixels[x, 1] == WHITE)

    if not all(valid_picture_feature_points):
        return 0

    not_run_feature_points = []
    for x in range(10, 47):
        for y in range(34, 37):
            not_run_feature_points.append(pixels[x, y] == BLACK)
    if all(not_run_feature_points):
        return 2

    run_feature_points = []
    for x in range(55, 76):
        for y in range(75, 79):
            run_feature_points.append(pixels[x, y] == BLACK)
    if all(run_feature_points):
        return 1

    return 0
