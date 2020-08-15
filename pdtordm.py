from flask import Flask, request
import requests, os

app = Flask(__name__, static_url_path='')

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

RDM_URL = "192.168.1.100:9001"
AUTH_TOKEN = 'YOURRDMTOKEN'

headers = {
    "User-Agent": "Python PDToRDM Connector V1.1",
    "Authorization": "Bearer " + AUTH_TOKEN
}

@app.route('/')
def homepage():
    return "Python PDToRDM Connector V1.1"

@app.route("/raw", methods=["POST"])
def raw():
    try:
        data = request.get_json(force=True)
        unique_id = request.headers.get('Origin')
        ip_address = request.environ['REMOTE_ADDR']
        user_agent = request.user_agent.string
        if isinstance(data, list):
            for proto in data:
                method = proto["type"]
                #print("[PDTORDM] %s - %s - %s" %(unique_id, ip_address, user_agent))
                #print("[PDTORDM] %s - %s" %(unique_id, method))
                if method == 2 or method == 106 or method == 102 or method == 104 or method == 101 or method == 156:
                    print("[PDTORDM] %s - %s - %s" %(unique_id, ip_address, user_agent))
                    print("[PDTORDM] %s - %s" %(unique_id, method))
                    req_rdm = handle_proto_data(proto, unique_id)
                    req = requests.post(url="http://"+RDM_URL+"/raw", json=req_rdm, headers=headers)
                    if req.status_code not in [200,201]:
                       print("[PDTORDM] Status code: {}".format(req.status_code))
        else:
            print("[PDTORDM] PogoDroid Protos Error")
    except requests.exceptions.ConnectionError as e:
        retry_error = True
        print("[PDTORDM] ERROR", e)
    return 'OK'

def handle_proto_data(proto, unique_id):
    # pull required data for rdm/ Trick rdm
    req_data = {}
    req_data["data"] = proto.pop("payload")
    req_data["method"] = proto.pop("type")
    # format data to rdm
    req_rdm = {"contents": []}
    req_rdm["contents"].append(req_data)
    req_rdm["username"] = unique_id
    req_rdm["trainerlvl"] = int(30)
    req_rdm["uuid"] = unique_id
    return req_rdm

if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000', debug=True)
