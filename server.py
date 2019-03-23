from flask import Flask, request, jsonify
from njupt import Card

app = Flask(__name__)


@app.route("/test")
def test():
    return "hello"


@app.route("/card/balance", methods=['POST'])
def card_balance():
    username = request.form['username']
    password = request.form['password']
    c = Card(account=username, password=password)
    return jsonify(c.get_balance())


@app.route("/card/recharge", methods=['POST'])
def card_recharge():
    amount = float(request.form['amount'])
    username = request.form['username']
    password = request.form['password']
    c = Card(account=username, password=password)
    return jsonify(c.recharge(amount=amount))


@app.route('/card/net_balance', methods=['POST'])
def card_net_balance():
    username = request.form['username']
    password = request.form['password']
    c = Card(username, password)
    return jsonify(c.get_net_balance())


@app.route('/card/recharge_net', methods=['POST'])
def card_recharge_net():
    username = request.form['username']
    password = request.form['password']
    c = Card(username, password)
    return jsonify(c.recharge_net())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
