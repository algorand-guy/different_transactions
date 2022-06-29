from algosdk import account, mnemonic
from algosdk.future import transaction
from utilities import CommonFunctions


# Declare application state storage (immutable)
local_ints = 1
local_bytes = 1
global_ints = 5
global_bytes = 5
global_schema = transaction.StateSchema (global_ints, global_bytes)
local_schema = transaction.StateSchema (local_ints, local_bytes)


# Declare the approval program
approval_program_source_initial =b"""#pragma version 6
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
int 4
==
txna ApplicationArgs 0
byte "Start the transaction"
==
&&
bnz main_l5
err
main_l5:
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


# create application
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
        print ("Created new app id: ", application_id)

        return application_id

    except Exception as error:
        print (error)


# group transactions
def app_call(client, passphrase, index):
    print (f"Calling {index} application...")

    # declare sender
    private_key = mnemonic.to_private_key (passphrase)
    sender = account.address_from_private_key (private_key)

    # get node suggested parameters
    params = client.suggested_params ()

    # declare references
    seller = "OLZBY2R7PFJN3DQ2JBLMT65O7IBZ4ARIFFUCRMZTVOCZ65JT53LD3UCIII"
    commission = "MO4CBXFLCK76E6VQJ3OLGS33ARGML2V2RGORIYNUSTJK4GVDKKL7LJDI3M"
    asset_id = 89120887

    # declare amount
    payment_amount = 100_000
    req_list = [CommonFunctions.percentage (90, payment_amount),
                CommonFunctions.percentage (10, payment_amount)]

    # Transaction 1: Application Call
    app_args = ["Start the transaction"]
    txn_1 = transaction.ApplicationNoOpTxn(sender, params, index, app_args)

    # Transaction 2: Payment to owner
    txn_2 = transaction.PaymentTxn(sender, params, seller, req_list[0])

    # Transaction 3: Payment for commission
    txn_3 = transaction.PaymentTxn(sender, params, commission, req_list[1])

    # Transaction 4: Asset Optin
    txn_4 = transaction.AssetTransferTxn(sender=sender, sp=params, index=asset_id, receiver=sender, amt=0)

    print("Grouping transactions...")
    # compute group id and put it into each transaction
    group_id = transaction.calculate_group_id([txn_1, txn_2, txn_3, txn_4])
    print("...computed groupId: ", group_id)
    txn_1.group = group_id
    txn_2.group = group_id
    txn_3.group = group_id
    txn_4.group = group_id

    print("Splitting unsigned transaction group...")
    # sign transactions
    print("Signing transactions...")
    stxn_1 = txn_1.sign(private_key)
    print("...account1 signed txn_1: ", stxn_1.get_txid())
    stxn_2 = txn_2.sign(private_key)
    print("...account2 signed txn_2: ", stxn_2.get_txid())
    stxn_3 = txn_3.sign(private_key)
    print("...account2 signed txn_3: ", stxn_3.get_txid())
    stxn_4 = txn_4.sign(private_key)
    print("...account2 signed txn_4: ", stxn_4.get_txid())

    # assemble transaction group
    print("Assembling transaction group...")
    signedGroup = [stxn_1, stxn_2, stxn_3, stxn_4]

    # send transactions
    print("Sending transaction group...")
    tx_id = client.send_transactions(signedGroup)

    # wait for confirmation

    confirmed_txn = CommonFunctions.wait_for_confirmation(client, tx_id)
    print("txID: {}".format(tx_id), " confirmed in round: {}".format(
        confirmed_txn.get("confirmed-round", 0)))

    return tx_id


if __name__ == "__main__":

    # Connect to algorand client
    algod_client = CommonFunctions.algo_conn()

    # Define account
    account_mnemonics = "program shy second strike ghost panel account fence welcome visa cattle sad cake proud reward lab abuse rail scare note alarm just cereal above cook"


    # Create application
    app_id = create_app(algod_client, account_mnemonics)

    # Call Application
    grp_tx_id = app_call(algod_client, account_mnemonics, app_id)
