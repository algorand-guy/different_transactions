import algosdk.encoding as e
from algosdk import account, mnemonic
from algosdk.future import transaction
from utilities import CommonFunctions


# Declare application state storage (immutable)
local_ints = 5
local_bytes = 5
global_ints = 10
global_bytes = 10
global_schema = transaction.StateSchema (global_ints, global_bytes)
local_schema = transaction.StateSchema (local_ints, local_bytes)

# Declare the approval program
approval_program_source_initial = b"""#pragma version 6
txn ApplicationID
int 0
==
bnz main_l6
txn OnCompletion
int NoOp
==
bnz main_l3
err
main_l3:
global GroupSize
int 1
==
txn Sender
global CreatorAddress
==
&&
txna ApplicationArgs 0
byte "Start the transaction"
==
&&
bnz main_l5
err
main_l5:
itxn_begin
int pay
itxn_field TypeEnum
txna Accounts 1
itxn_field Receiver
txna ApplicationArgs 1
btoi
itxn_field Amount
int 1000
itxn_field Fee
itxn_next
int pay
itxn_field TypeEnum
txna Accounts 2
itxn_field Receiver
txna ApplicationArgs 2
btoi
itxn_field Amount
int 1000
itxn_field Fee
itxn_next
int axfer
itxn_field TypeEnum
txna Accounts 0
itxn_field AssetReceiver
int 0
itxn_field AssetAmount
txna Assets 0
itxn_field XferAsset
int 1000
itxn_field Fee
itxn_submit
int 1
return
main_l6:
int 1
return
"""

# Declare clear state program source
clear_program_source = b"""#pragma version 6
int 1
"""


def create_app(client, passphrase):
    print ("Creating application...")

    # declare accounts
    private_key = mnemonic.to_private_key (passphrase)
    address = account.address_from_private_key (private_key)

    # compile the smart contracts
    approval_program = CommonFunctions.compile_program (client, approval_program_source_initial)
    clear_program = CommonFunctions.compile_program (client, clear_program_source)

    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params ()

    txn = transaction.ApplicationCreateTxn (address, params, on_complete,
                                            approval_program, clear_program,
                                            global_schema, local_schema)

    # sign transaction
    print ("Signing Transaction!")
    signed_txn = txn.sign (private_key)
    tx_id = signed_txn.transaction.get_txid ()

    try:
        # send the transaction to the network
        client.send_transactions ([signed_txn])

        # await confirmation
        CommonFunctions.wait_for_confirmation (client, tx_id)
        transaction_response = client.pending_transaction_info (tx_id)
        application_id = transaction_response['application-index']
        print ("Created new user id: ", application_id)

        return application_id

    except Exception as error:
        print (error)


# Call the smart contract
def call_smart_contract(client, passphrase, index, args_list):
    print (f"Calling {index} application...")

    # declare sender
    private_key = mnemonic.to_private_key (passphrase)
    sender = account.address_from_private_key (private_key)

    # get node suggested parameters
    params = client.suggested_params ()

    # create unsigned transaction
    app_args = ["Start the transaction", int (args_list[0]), int (args_list[1])]

    # declare account reference
    seller = "OLZBY2R7PFJN3DQ2JBLMT65O7IBZ4ARIFFUCRMZTVOCZ65JT53LD3UCIII"
    commission = "MO4CBXFLCK76E6VQJ3OLGS33ARGML2V2RGORIYNUSTJK4GVDKKL7LJDI3M"
    accounts_lst = [seller, commission]
    asset_lst = [89120887]

    # performing transaction
    txn = transaction.ApplicationNoOpTxn (sender, params, index, app_args, accounts=accounts_lst,
                                          foreign_assets=asset_lst)

    # sign transaction
    print ("Signing Transaction!")
    signed_txn = txn.sign (private_key)
    tx_id = signed_txn.transaction.get_txid ()

    try:
        # send the transaction to the network
        client.send_transactions ([signed_txn])

        # await confirmation
        confirmed_txn = CommonFunctions.wait_for_confirmation (client, tx_id)
        print ("Result confirmed in round: {}".format (confirmed_txn['confirmed-round']))
    except Exception as error:
        print (error)

    return tx_id


# run the application
if __name__ == "__main__":
    # define the client
    algod_client = CommonFunctions.algo_conn ()

    # Define account
    account_mnemonics = "program shy second strike ghost panel account fence welcome visa cattle sad cake proud reward lab abuse rail scare note alarm just cereal above cook"

    # create application
    app_id = create_app (algod_client, account_mnemonics)

    # smart contract address
    smart_contract_address = e.encode_address (e.checksum (b'appID' + app_id.to_bytes (8, 'big')))
    print (f"Fund the address, use the link https://bank.testnet.algorand.network/ : {smart_contract_address}")
    input ("Press ENTER to continue...")

    # get the balance of the smart contract
    account_info = algod_client.account_info (smart_contract_address)
    print (f"Account balance: {account_info.get ('amount')} microAlgos")

    # inner transaction details
    payment_amount = 100_000
    req_list = [CommonFunctions.percentage (90, payment_amount),
                CommonFunctions.percentage (10, payment_amount)]

    # call the smart contract
    call_smart_contract (algod_client, account_mnemonics, app_id, req_list)
