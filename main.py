from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.rpc.types import MemcmpOpts
import base64
import json
from rich import print

# === CONFIG ===
RPC_URL = "https://api.mainnet-beta.solana.com"
TOKEN_MINT = "EgixdvE18LuQS5RxkgBwG7JRULv3Cb4k4g3cHu1Cpump"  # Ganti dengan token pump.fun Anda

client = Client(RPC_URL)

def get_token_supply(mint_address):
    resp = client.get_token_supply(PublicKey(mint_address))
    if resp["result"]:
        amount = int(resp["result"]["value"]["amount"])
        decimals = int(resp["result"]["value"]["decimals"])
        return amount / (10 ** decimals), decimals
    return None, None

def get_token_holders(mint_address):
    # Ambil semua account pemilik token
    filters = [
        {"dataSize": 165},
        {"memcmp": {"offset": 0, "bytes": mint_address}}
    ]
    result = client.get_program_accounts(PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                                         encoding="jsonParsed", filters=filters)
    holders = 0
    top_holder_amount = 0
    for acc in result["result"]:
        data = acc["account"]["data"]["parsed"]["info"]
        amount = int(data["tokenAmount"]["amount"])
        if amount > 0:
            holders += 1
            top_holder_amount = max(top_holder_amount, amount)
    return holders, top_holder_amount

def estimate_marketcap(price, supply):
    return price * supply

def check_100x(price, supply):
    now_mc = estimate_marketcap(price, supply)
    mc_100x = now_mc * 100
    price_100x = price * 100
    return now_mc, mc_100x, price_100x

def main():
    print("[bold cyan]🚀 Analisa Token Pump.fun via Solana RPC[/bold cyan]")
    print(f"[bold]Token Mint:[/bold] {TOKEN_MINT}")

    # === Supply & Decimals ===
    supply, decimals = get_token_supply(TOKEN_MINT)
    print(f"[green]Total Supply:[/green] {supply:,.0f} (Decimals: {decimals})")

    # === Holders ===
    holders, top_holder = get_token_holders(TOKEN_MINT)
    top_percent = (top_holder / (supply * (10 ** decimals))) * 100
    print(f"[green]Jumlah Holder:[/green] {holders}")
    print(f"[green]Top Holder:[/green] {top_percent:.2f}% dari total supply")

    # === Harga Sekarang (masih dummy, ganti dengan perhitungan dari pool Raydium jika mau akurat) ===
    # Misalnya: diasumsikan harga token $0.00001
    current_price = 0.00001
    now_mc, mc_100x, price_100x = check_100x(current_price, supply)

    print(f"[yellow]Harga Sekarang:[/yellow] ${current_price:,.8f}")
    print(f"[yellow]Market Cap Saat Ini:[/yellow] ${now_mc:,.2f}")
    print(f"[bold magenta]🎯 Target 100x:[/bold magenta] Harga: ${price_100x:,.5f} | Market Cap: ${mc_100x:,.2f}")
    print(f"[bold green]✅ Potensi 100x: {'YA' if mc_100x < 10_000_000 else 'TIDAK (sudah terlalu besar)'}[/bold green]")

if __name__ == "__main__":
    main()
