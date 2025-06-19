from solders.pubkey import Pubkey as PublicKey
from solana.rpc.api import Client
from rich import print

client = Client("https://api.mainnet-beta.solana.com")

mint_address = PublicKey.from_string("EgixdvE18LuQS5RxkgBwG7JRULv3Cb4k4g3cHu1Cpump")

def get_token_info(mint: PublicKey):
    # Ambil total supply token
    resp = client.get_token_supply(mint)

    if not resp.value:
        print("[red]Token tidak ditemukan atau tidak valid.[/red]")
        return

    amount = int(resp.value.amount)
    decimals = resp.value.decimals
    total_supply = amount / (10 ** decimals)

    print(f"[green]Supply:[/green] {total_supply:,.2f}")
    print(f"[green]Decimals:[/green] {decimals}")

get_token_info(mint_address)
