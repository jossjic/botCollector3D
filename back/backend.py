import flask
from flask.json import jsonify
import uuid
from incinerador import Sala

games = {}

app = flask.Flask(__name__)

@app.route("/games", methods=["POST"])
def create():
    global games
    id = str(uuid.uuid4())
    games[id] = Sala()
    lista = []
    for bot in games[id].schedule.agents:
        lista.append({"id": bot.unique_id, "x": bot.pos[0], "z": bot.pos[1]})

    # response = flask.make_response()
    # response.headers['Location'] = f"/games/{id}"
    # response.status_code = 201
    # response.data = jsonify(lista)
    # return response
    return jsonify(lista), 201, {'Location': f"/games/{id}"}

@app.route("/games/<id>", methods=["GET"])
def queryState(id):
    global model
    model = games[id]
    model.step()
    lista = []
    for bot in model.schedule.agents:
        lista.append({"id": bot.unique_id, "x": bot.pos[0], "z": bot.pos[1]})
    return jsonify(lista)

app.run()