from flask import Flask, request
import requests, os
import urllib3

import base64
from pogoprotos.POGOProtos.Rpc_pb2 import GetMapObjectsOutProto, EncounterOutProto, GetHoloholoInventoryOutProto, \
     FortSearchOutProto, FortDetailsOutProto, GymGetInfoOutProto, GetPlayerOutProto, ItemProto, InventoryItemProto, InventoryDeltaProto, HoloInventoryItemProto, Item

#from pogoprotos.networking.responses.get_map_objects_response_pb2 import GetMapObjectsResponse #106
#from pogoprotos.networking.responses.encounter_response_pb2 import EncounterResponse #102
#from pogoprotos.networking.responses.get_holo_inventory_response_pb2 import GetHoloInventoryResponse #4
#from pogoprotos.networking.responses.fort_search_response_pb2 import FortSearchResponse #101
#from pogoprotos.networking.responses.fort_details_response_pb2 import FortDetailsResponse #104
#from pogoprotos.networking.responses.gym_get_info_response_pb2 import GymGetInfoResponse # 156
#from pogoprotos.networking.responses.get_player_response_pb2 import GetPlayerResponse #2

from google.protobuf.json_format import MessageToDict
import pprint

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
    data = request.get_json(force=True)
    unique_id = request.headers.get('Origin')
    ip_address = request.environ['REMOTE_ADDR']
    user_agent = request.user_agent.string

    if isinstance(data, list):
        for proto in data:
            itemID, count = decode(proto, unique_id)
            lureInfo = ''
            if itemID == 'ITEM_TROY_DISK' or itemID == 'ITEM_TROY_DISK_GLACIAL' or itemID == 'ITEM_TROY_DISK_MOSSY' or itemID == 'ITEM_TROY_DISK_MAGNETIC' or itemID == 'ITEM_TROY_DISK_RAINY':
                #print(itemID, count)
                lureInfo = unique_id+' '+itemID+' '+str(count)
            #print(lureInfo)
            method = proto["type"]
            if method == 2 or method == 4 or method == 106 or method == 102 or method == 145 or method == 104 or method == 101 or method == 156:
                #decode(proto, method, unique_id)
                req_rdm = handle_proto_data(proto, unique_id)
                try:
                    req = requests.post(url="http://"+RDM_URL+"/raw", json=req_rdm, headers=headers, timeout=1)
                    if req.status_code not in [200,201]:
                       print("[PDTORDM] Status code: {}".format(req.status_code))
                    print("[PDTORDM] /RAW", unique_id, ip_address, method, lureInfo)
                except urllib3.exceptions.ProtocolError as de:
                    retry_error = True
                    print("[PDTORDM] RAW ERROR:", de)
                except requests.exceptions.ConnectionError as e:
                    retry_error = True
                    print("[PDTORDM] RAW ERROR", e)
    else:
        print("[PDTORDM] PogoDroid Protos Error")

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

def decode(proto, unique_id):
    #if unique_id == 'SMA520W':
    itemID = None 
    count = None
    try:
        Decode = base64.b64decode(proto['payload'])
        if proto["type"] == 4:
            obj = GetHoloholoInventoryOutProto()
            obj.ParseFromString(Decode)
            object = MessageToDict(obj)
            inventoryDelta = object.get('inventoryDelta')
            inventoryItem = inventoryDelta.get('inventoryItem')
            for data in inventoryItem:
                inventoryItemData = data.get('inventoryItemData')
                item = inventoryItemData.get('item')
                if item is not None:
                    itemID = item.get('itemId')
                    count = item.get('count')
        #print(itemID, count)
        return itemID, count

    except urllib3.exceptions.ProtocolError as de:
        retry_error = True
        print("[GDSTORDM] DECODE ERROR:", de)
    except requests.exceptions.ConnectionError as ce:
        retry_error = True
        print("[GDSTORDM] Requests ERROR:", ce)
    except TypeError as t:
        print("[GDSTORDM] TypeError ERROR: {}".format(t))
    except AssertionError as a:
        print("[GDSTORDM] AssertionError ERROR: {}".format(a))

#def decode(proto, method, unique_id):
#    try:
#        if method == 106 and unique_id == 'SMG928W8':
#            Decode = base64.b64decode(proto['payload'])
#            obj = GetMapObjectsOutProto()
#            obj.ParseFromString(Decode)
#            object = MessageToDict(obj)
#            mapCells = object.get('mapCells')
#            for forts in mapCells:
#                fort = forts.get('fort')
#                if fort:
#                    type = str()
#                    for type in fort:
#                        type = type.get('type')
#                    if type != 'CHECKPOINT':
#                        pprint.pprint(fort)

#    except urllib3.exceptions.ProtocolError as de:
#        retry_error = True
#        print("[GDSTORDM] DECODE ERROR:", de)
#    except requests.exceptions.ConnectionError as ce:
#        retry_error = True
#        print("[GDSTORDM] Requests ERROR:", ce)
#    except TypeError as t:
#        print("[GDSTORDM] TypeError ERROR: {}".format(t))
#    except AssertionError as a:
#        print("[GDSTORDM] AssertionError ERROR: {}".format(a))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000', debug=True)
