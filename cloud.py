import os
from datetime import datetime

import leancloud
from PIL import Image

from shortcut_api import timezone
from utils import qzone
from utils import qzone_login
from utils.store import save_qq_cookies, fetch_qq_cookies, save_run_status, RunStatusEnum

engine = leancloud.Engine()

today = datetime.today().strftime('%Y-%m-%d')  # '2019-03-27'

QQ_NUMBER = os.environ['LEANCLOUD_QQ_NUMBER']
QQ_PASSWORD = os.environ['LEANCLOUD_QQ_PASSWORD']
TARGET_QQ = os.environ.get('LEANCLOUD_TARGET_QQ', 2563280140)


@engine.define
def init_qq_cookies():
    for i in range(10):
        cookies = qzone_login.login(QQ_NUMBER, QQ_PASSWORD)
        if not cookies.get('p_skey'):
            leancloud.logger.critical('获取cookie失败')
            continue
        save_qq_cookies(cookies)
        break


@engine.define
def check_run():
    today = datetime.now(tz=timezone)
    today_str = today.strftime("%Y-%m-%d")
    cookies = fetch_qq_cookies()
    q = qzone.Qzone(**cookies)
    emotions = q.emotion_list(TARGET_QQ, num=20)
    for emotion in emotions:
        if datetime.fromtimestamp(emotion.ctime, timezone).date() != today.date():
            break
        for pic in emotion.pictures:
            result = run(pic)
            if result == RunStatusEnum.UNKNOWN:
                continue
            save_run_status(date=today_str, run_status=result.value)
            return

    save_run_status(date=today_str, run_status=RunStatusEnum.UNKNOWN.value)


def run(pic):
    """
    判断图片， 是跑还是不跑
    """
    WHITE = 255
    BLACK = 0
    image = Image.open(pic.open()).resize((100, 100)).convert('L')
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            pixels[x, y] = BLACK if pixels[x, y] < 20 else WHITE

    valid_picture_feature_points = []
    for x in range(image.width):
        valid_picture_feature_points.append(pixels[x, 1] == WHITE)

    if not all(valid_picture_feature_points):
        return RunStatusEnum.UNKNOWN

    not_run_feature_points = []
    for x in range(10, 47):
        for y in range(34, 37):
            not_run_feature_points.append(pixels[x, y] == BLACK)
    if all(not_run_feature_points):
        return RunStatusEnum.NOT_RUN

    run_feature_points = []
    for x in range(55, 76):
        for y in range(75, 79):
            run_feature_points.append(pixels[x, y] == BLACK)
    if all(run_feature_points):
        return RunStatusEnum.NOT_RUN

    return RunStatusEnum.UNKNOWN
