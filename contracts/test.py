import os

from pyteal import *


def contract():

    # Checks that the sender is the app creator
    is_app_creator = Txn.sender() == Global.creator_address()

    app_args = Txn.application_args

    inner_txn = Seq(
        InnerTxnBuilder.Begin (),

        # Transaction 1: 90% Payment to Account A
        InnerTxnBuilder.SetFields({
            TxnField.type_enum:TxnType.Payment,
            TxnField.sender: Global.creator_address(),
            TxnField.receiver: Bytes("OLZBY2R7PFJN3DQ2JBLMT65O7IBZ4ARIFFUCRMZTVOCZ65JT53LD3UCIII"),
            TxnField.amount: Btoi(app_args[2]),
        }),

        # Transaction 2: 10% Payment to Account B
        InnerTxnBuilder.Next(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum:TxnType.Payment,
            TxnField.sender: Global.creator_address(),
            TxnField.receiver: Bytes("MO4CBXFLCK76E6VQJ3OLGS33ARGML2V2RGORIYNUSTJK4GVDKKL7LJDI3M"),
            TxnField.amount: Btoi(app_args[4]),
        }),

        # Submit the transaction
        InnerTxnBuilder.Submit(),
        Approve ()
    )


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

