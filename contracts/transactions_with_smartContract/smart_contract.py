from pyteal import *


def contract():

    group_transaction = Cond(
        [And(
            Global.group_size() == Int(4),
            Txn.application_args[0] == Bytes("Start the transaction")
        ), Approve()]
    )

    program = Cond(
        [Txn.application_id() == Int(0), Approve()],
        [Txn.on_completion() == OnComplete.NoOp, group_transaction]
    )

    return program


if __name__ == "__main__":
    with open("smart_contract.teal", "w") as f:
        compiled = compileTeal(contract(), mode=Mode.Application, version=6)
        f.write(compiled)