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


@app.route("/card/recharge", method=['POST'])
def card_recharge():
    amount = float(request.form['amount'])
    username = request.form['username']
    password = request.form['password']
    c = Card(account=username, password=password)
    return jsonify(c.recharge(amount=amount))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
