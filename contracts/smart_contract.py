import os

from pyteal import *


def contract():

    # Checks that the sender is the app creator
    is_app_creator = Txn.sender() == Global.creator_address()

    app_args = Txn.application_args

    inner_txn = Seq(
        InnerTxnBuilder.Begin (),

        # Transaction 1: 90% of Payment to seller
        InnerTxnBuilder.SetFields({
            TxnField.type_enum:TxnType.Payment,
            TxnField.receiver: Txn.accounts[1],
            TxnField.amount: Btoi(app_args[1]),
            TxnField.fee: Int(1000)
        }),

        # Transaction 2: 10% of Payment for commission
        InnerTxnBuilder.Next(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum:TxnType.Payment,
            TxnField.receiver: Txn.accounts[2],
            TxnField.amount: Btoi(app_args[2]),
            TxnField.fee: Int(1000)
        }),

        # Transaction 3: Asset Optin Transaction
        InnerTxnBuilder.Next(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum:TxnType.AssetTransfer,
            TxnField.asset_receiver: Txn.accounts[0],
            TxnField.asset_amount: Int(0),
            TxnField.xfer_asset: Txn.assets[0],
            TxnField.fee: Int(1000)
        }),

            # Submit the transaction
            InnerTxnBuilder.Submit(),
        Approve ()
    )

    # check the conditions to run the transaction
    group_transaction = Cond(
        [And(
            Global.group_size() == Int(1),
            is_app_creator,
            app_args[0] == Bytes("Start the transaction")
        ), inner_txn]
    )

    program = Cond(
        [Txn.application_id() == Int(0), Approve()],
        [Txn.on_completion() == OnComplete.NoOp, group_transaction]
    )

    return program


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path,"smart_contract.teal"), "w") as f:
        f.write(compileTeal(contract(), mode=Mode.Application, version=6))

