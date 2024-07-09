import bittensor
from bittensor.commands import (
    ScheduleColdKeySwapCommand,
)
from tests.e2e_tests.utils import (
    setup_wallet,
)


def test_schedule_coldkey_swap(local_chain, capsys):
    # Register root as Alice
    alice_keypair, alice_exec_command, alice_wallet_path = setup_wallet("//Alice")
    bob_keypair, bob_exec_command, bob_wallet_path = setup_wallet("//Bob")

    block = local_chain.query(
        "SubtensorModule", "ColdkeyArbitrationBlock", [alice_keypair.ss58_address]
    )

    assert block == 0

    alice_exec_command(
        ScheduleColdKeySwapCommand,
        [
            "wallet",
            "schedule_coldkey_swap",
            "--new_coldkey",
            bob_keypair.ss58_address,
            "--prompt",
            "False",
        ],
    )
    output = capsys.readouterr().out
    assert (
        "Good news. There has been no previous key swap initiated for your coldkey swap."
        in output
    )

    subtensor = bittensor.subtensor(network="ws://localhost:9945")

    # verify current balance
    block = subtensor.check_in_arbitration(alice_keypair.ss58_address)

    # assert block == 1

    alice_exec_command(
        ScheduleColdKeySwapCommand,
        [
            "wallet",
            "schedule_coldkey_swap",
            "--new_coldkey",
            bob_keypair.ss58_address,
        ],
    )

    output = capsys.readouterr().out
    assert "There has been a swap request made for this key previously." in output
    block = local_chain.query(
        "SubtensorModule", "ColdkeyArbitrationBlock", [alice_keypair.ss58_address]
    )

    assert block == 2

    alice_exec_command(
        ScheduleColdKeySwapCommand,
        [
            "wallet",
            "schedule_coldkey_swap",
            "--new_coldkey",
            bob_keypair.ss58_address,
        ],
    )

    output = capsys.readouterr().out
    assert "This key is currently in arbitration." in output
