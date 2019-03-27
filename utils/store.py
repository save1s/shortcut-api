from enum import Enum

import leancloud

RunRecord = leancloud.Object.extend('RunRecord')
Config = leancloud.Object.extend('Config')


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
