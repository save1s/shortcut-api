from flask import Flask, request, jsonify, Response
from njupt import Card, Zhengfang
from njupt.exceptions import AuthenticationException
from functools import wraps
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import json
import base64

term_start_date = datetime(2019, 2, 18, tzinfo=pytz.timezone("Asia/Shanghai"))

app = Flask(__name__)


ClassTime = {
    1:  term_start_date + timedelta(hours=8),
    2:  term_start_date + timedelta(hours=8, minutes=50),
    3:  term_start_date + timedelta(hours=9, minutes=50),
    4:  term_start_date + timedelta(hours=10, minutes=40),
    5:  term_start_date + timedelta(hours=11, minutes=30),
    6:  term_start_date + timedelta(hours=13, minutes=45),
    7:  term_start_date + timedelta(hours=14, minutes=35),
    8:  term_start_date + timedelta(hours=15, minutes=35),
    9:  term_start_date + timedelta(hours=16, minutes=25),
    10:  term_start_date + timedelta(hours=18, minutes=30),
    11:  term_start_date + timedelta(hours=19, minutes=25),
    12:  term_start_date + timedelta(hours=20, minutes=20),
}


def data_acccess(f):
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
            return jsonify({'success': False, 'message': '账号或密码有误', 'data': {}})
        except Exception as e:
            return jsonify({'success': False, 'message': e, 'data': {}})

    return wrapper


@app.route("/")
def test():
    return "A save1s.com project."


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
@data_acccess
def card_balance():
    return jsonify(request.card.get_balance())


@app.route("/card/recharge", methods=['POST'])
@data_acccess
def card_recharge():
    amount = float(request.form['amount'])
    return jsonify(request.card.recharge(amount=amount))


@app.route('/card/net_balance', methods=['POST'])
@data_acccess
def card_net_balance():
    return jsonify(request.card.get_net_balance())


@app.route('/card/recharge_net', methods=['POST'])
@data_acccess
def card_recharge_net():
    amount = float(request.form['amount'])
    return jsonify(request.card.recharge_net(amount=amount))


@app.route('/card/recharge_elec', methods=['POST'])
@data_acccess
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
        return jsonify({
            'success': result['success'],
            'data': {},
            'message': result['msg'],
        })
    if school_area == "仙林":
        result = request.card.recharge_xianlin_elec(
            amount=amount,
            building_name=building,
            big_room_id=big_room_id,
            small_room_id=small_room_id
        )
        return jsonify({
            'success': result['success'],
            'data': {},
            'message': result['msg'],
        })
    return jsonify({'success': False, 'message': '错误的校区', 'data': {}})


@app.route('/zhengfang/courses', methods=['POST'])
@data_acccess
def zhengfang_courses():
    return jsonify(request.zhengfang.get_courses())


@app.route('/zhengfang/courses/ical', methods=['POST'])
@data_acccess
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
    return(base64.urlsafe_b64encode(cal.to_ical()))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
