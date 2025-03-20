from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/getServer', methods=['GET'])
def get_server():
    return jsonify({"code": 200, "server": "localhost:3001"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)