import leancloud
from enum import Enum

from leancloud import Engine

engine = Engine()

RunRecord = leancloud.Object.extend('RunRecord')


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
