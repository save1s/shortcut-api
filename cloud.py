import leancloud
from enum import Enum

from leancloud import Engine

engine = Engine()

RunRecord = leancloud.Object.extend('RunRecord')
QQCookies = leancloud.Object.extend('QQCookies')


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


def save_qq_cookies(date, cookies):
    """

    :param date: 如 "2019-01-01"
    :param cookies: dict
    :return:
    """
    query = QQCookies.query
    query.equal_to('date', date)
    qq_cookies_list = query.find()
    if qq_cookies_list:
        qq_cookies = qq_cookies_list[0]
    else:
        qq_cookies = QQCookies()
        qq_cookies.set('date', date)
    qq_cookies.set('cookies', cookies)
    qq_cookies.save()


def get_qq_cookies(date):
    """

    :param date:
    :return:
    """
    query = QQCookies.query
    query.equal_to('date', date)
    qq_cookies_list = query.find()
    if qq_cookies_list:
        qq_cookies = qq_cookies_list[0]
        return qq_cookies.get('cookies')
    else:
        return {}
