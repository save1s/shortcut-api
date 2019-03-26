from datetime import datetime

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
    pass
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


@engine.define
def test_store(**params):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_run_status(now, RunStatusEnum.RUN)
