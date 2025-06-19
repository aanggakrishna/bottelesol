from solders.pubkey import Pubkey as PublicKey
from solana.rpc.api import Client
from rich import print

# Ganti endpoint jika Anda pakai RPC sendiri
client = Client("https://api.mainnet-beta.solana.com")

# Ganti dengan address token/mint Pump.fun
mint_address = PublicKey.from_string("EgixdvE18LuQS5RxkgBwG7JRULv3Cb4k4g3cHu1Cpump")

def get_token_info(mint: PublicKey):
    # Total supply token
    supply_data = client.get_token_supply(mint)
    if not supply_data["result"]:
        print("[red]Token tidak ditemukan.[/red]")
        return

    supply = int(supply_data["result"]["value"]["amount"])
    decimals = int(supply_data["result"]["value"]["decimals"])

    print(f"[green]Supply:[/green] {supply / (10 ** decimals):,.2f}")
    print(f"[green]Decimals:[/green] {decimals}")

    # Optional: cari info lain seperti owner, metadata, dsb
    # Bisa ditambah dengan parsing data dari get_account_info atau on-chain parser

get_token_info(mint_address)
