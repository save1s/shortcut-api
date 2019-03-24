from flask import Flask, request, jsonify
from njupt import Card, Zhengfang
from njupt.exceptions import AuthenticationException
from functools import wraps

app = Flask(__name__)


def data_acccess(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            account = request.form['account']
            password = request.form['password']
            if '/card/' in request.path:
                request.card = Card(account=account, password=password)
            if '/zhengfang/' in request.path:
                request.zhengfang = Zhengfang(account=account, password=password)
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
    # todo
    pass


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
