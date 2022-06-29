import base64
import os
from algosdk.v2client import algod



# Connection to the algorand network
def algo_conn():
    algod_address = "https://testnet-algorand.api.purestake.io/ps2"
    algod_token = "K7DgVll3W19DdHA3FTduX4XZTuCvTFf32HXUP5E4"
    headers = {"X-API-Key": algod_token}
    conn = algod.AlgodClient(algod_token, algod_address, headers)

    return conn


# compile program used to compile the source code, used when new application is created
def compile_program(client, source_code):
    compile_response = client.compile(source_code.decode('utf-8'))
    return base64.b64decode(compile_response['result'])


# helper function that waits for a given txid to be confirmed by the network
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
        print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
        return txinfo


# load resource used for logic signature
def load_resource(res):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, res)
    with open(path, "rb") as fin:
        data = fin.read()
    return data


# find the part of the number
def percentage(part, whole):
    result = part * float(whole)/100
    return int(result)


