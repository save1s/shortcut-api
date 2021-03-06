import base64
from datetime import datetime, timedelta
from functools import wraps
import pytz
from flask import Flask, request, jsonify, Response
from icalendar import Calendar, Event
from njupt import Card, Zhengfang, RunningMan
from njupt.exceptions import AuthenticationException, NjuptException

from utils.store import get_run_status, RunStatusEnum

timezone = pytz.timezone("Asia/Shanghai")
term_start_date = datetime(2019, 2, 18, tzinfo=timezone)

app = Flask(__name__)

ClassTime = {
    1: term_start_date + timedelta(hours=8),
    2: term_start_date + timedelta(hours=8, minutes=50),
    3: term_start_date + timedelta(hours=9, minutes=50),
    4: term_start_date + timedelta(hours=10, minutes=40),
    5: term_start_date + timedelta(hours=11, minutes=30),
    6: term_start_date + timedelta(hours=13, minutes=45),
    7: term_start_date + timedelta(hours=14, minutes=35),
    8: term_start_date + timedelta(hours=15, minutes=35),
    9: term_start_date + timedelta(hours=16, minutes=25),
    10: term_start_date + timedelta(hours=18, minutes=30),
    11: term_start_date + timedelta(hours=19, minutes=25),
    12: term_start_date + timedelta(hours=20, minutes=20),
}


@app.errorhandler(NjuptException)
def all_exception_handler(e):
    app.logger.exception(e)
    return Result.failure(message="NJUPT接口请求异常, 请重试", data={'error': str(e)})


class Result:

    @classmethod
    def result(cls, success, message, data):
        return jsonify({
            'success': success,
            'message': message,
            'data': data,
        })

    @classmethod
    def success(cls, message, data):
        return cls.result(
            success=True,
            message=message,
            data=data
        )

    @classmethod
    def failure(cls, message, data):
        return cls.result(
            success=False,
            message=message,
            data=data
        )


def data_access(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            account = request.form['account']
            password = request.form['password']
            if '/card/' in request.path:
                request.card = Card(account=account, password=password)
            if '/zhengfang/' in request.path:
                request.zhengfang = Zhengfang(
                    account=account, password=password)
            # else:
            #     raise Exception
            return f()
        except AuthenticationException:
            return Result.failure(message='账号或密码有误', data=None)

    return wrapper


def is_today(a_datetime):
    current_date = datetime.now(timezone)
    return a_datetime.date() == current_date.date()


def is_same_day(datetime1, datetime2):
    return datetime1.date() == datetime2.date()


@app.route("/")
def test():
    return Result.success(
        message="A save1s project.",
        data={'url': 'https://github.com/save1s'}
    )


@app.route("/base64/<string>")
def base64_decode(string):
    data = base64.urlsafe_b64decode(string).decode('utf-8')
    return Response(
        data,
        content_type='text/calendar',
        headers={
            "Content-Disposition":
                "attachment;filename=iCal.ics"
        }
    )


@app.route("/card/balance", methods=['POST'])
@data_access
def card_balance():
    return Result.success(message='查询成功', data=request.card.get_balance())


@app.route("/card/recharge", methods=['POST'])
@data_access
def card_recharge():
    amount = float(request.form['amount'])
    result = request.card.recharge(amount=amount)
    return Result.result(
        success=result['success'],
        message=result['msg'],
        data=None
    )


@app.route('/card/net_balance', methods=['POST'])
@data_access
def card_net_balance():
    return Result.success(message='查询成功', data=request.card.get_net_balance())


@app.route('/card/recharge_net', methods=['POST'])
@data_access
def card_recharge_net():
    amount = float(request.form['amount'])
    result = request.card.recharge_net(amount=amount)
    return Result.result(
        success=result['success'],
        message=result['msg'],
        data=None
    )


@app.route('/card/recharge_elec', methods=['POST'])
@data_access
def card_recharge_elec():
    amount = float(request.form['amount'])
    school_area = request.form['school_area']
    building = request.form['building']
    big_room_id = int(request.form['big_room_id'])
    small_room_id = int(request.form['small_room_id'])
    if school_area == "三牌楼":
        result = request.card.recharge_sanpailou_elec(
            amount=amount,
            building_name=building,
            room_id="{}{}".format(big_room_id, small_room_id)
        )
        return Result.result(
            success=result['success'],
            message=result['msg'],
            data=None
        )
    if school_area == "仙林":
        result = request.card.recharge_xianlin_elec(
            amount=amount,
            building_name=building,
            big_room_id=big_room_id,
            small_room_id=small_room_id
        )
        return Result.result(
            success=result['success'],
            message=result['msg'],
            data=None
        )
    return Result.failure(message='错误的校区', data=None)


@app.route('/zhengfang/courses', methods=['POST'])
@data_access
def zhengfang_courses():
    return jsonify(request.zhengfang.get_courses())


@app.route('/zhengfang/courses/ical', methods=['POST'])
@data_access
def zhengfang_courses_ical():
    courses = request.zhengfang.get_courses()
    cal = Calendar()
    cal.add('prodid', '-//save1s.com//NJUPT Calendar//')
    cal.add('version', '2.0')
    for course in courses:
        class_start_time = ClassTime.get(course['class_start'], 1) \
                           + timedelta(days=course['day'] - 1) \
                           + timedelta(weeks=course['week_start'] - 1)
        class_end_time = ClassTime.get(course['class_end'], 2) \
                         + timedelta(days=course['day'] - 1) \
                         + timedelta(weeks=course['week_start'] - 1) \
                         + timedelta(minutes=45)
        event = Event()
        event.add('summary', course['name'])
        event.add('location', course['room'] + ' ' + course['teacher'])
        event.add('dtstart', class_start_time)
        event.add('dtend', class_end_time)
        event.add('rrule', {
            'freq': 'weekly',
            'interval': course['interval'],
            'count': (course['week_end'] + 1) // 2
        })
        cal.add_component(event)
    return (base64.urlsafe_b64encode(cal.to_ical()))


@app.route('/runningman', methods=['POST'])
def check_morning_exercise():
    student_id = request.form['student_id']
    name = request.form['name']
    running_man = RunningMan(student_id, name)
    try:
        exercise_dict = running_man.check()
    except AuthenticationException as e:
        return Result.failure(message=str(e), data=None)
    origin_number = exercise_dict['origin_number']
    extra_number = exercise_dict['extra_number']
    date_list = exercise_dict['date_list']

    total_number = origin_number + extra_number

    recent_records = []
    if not date_list:
        msg = '这学期还没有跑过操'
    if len(date_list) == 1:
        if is_today(date_list[0]):
            msg = '今天只打了一次卡'
        else:
            msg = '今天没打卡'
        recent_records.extend(date_list)
    elif len(date_list) >= 2:
        if is_same_day(date_list[0], date_list[1]) and is_today(date_list[0]):
            msg = '今天打卡了'
        elif is_today(date_list[0]) and not is_same_day(date_list[0], date_list[1]):
            msg = '今天只打了一次卡'
        else:
            msg = '今天没打卡'
        recent_records.extend(date_list[:2])

    recent_records = list(
        map(lambda t: t.strftime('%Y年%m月%d日 %H时%M分'), recent_records))
    return Result.success(
        message=msg,
        data={
            'total_number': total_number,
            'recent_records': recent_records
        }
    )


@app.route('/check_running')
def check_running():
    status = get_run_status(datetime.now(timezone).strftime("%Y-%m-%d"))
    if status == RunStatusEnum.RUN:
        return Result.success(message="跑", data=None)
    if status == RunStatusEnum.NOT_RUN:
        return Result.success(message="不跑", data=None)
    return Result.success(message="我也不知道", data=None)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
