from solana.rpc.api import Client
from solders.pubkey import Pubkey
from rich import print

client = Client("https://api.mainnet-beta.solana.com")

# Ganti dengan token yang ingin dianalisis (dari Pump.fun atau lainnya)
mint_address = Pubkey.from_string("EgixdvE18LuQS5RxkgBwG7JRULv3Cb4k4g3cHu1Cpump")


def get_token_info(mint: Pubkey):
    supply_resp = client.get_token_supply(mint)

    if not supply_resp.value:
        print("[red]Token tidak ditemukan atau tidak valid.[/red]")
        return None

    amount = int(supply_resp.value.amount)
    decimals = supply_resp.value.decimals
    total_supply = amount / (10 ** decimals)

    print(f"[green]Total Supply:[/green] {total_supply:,.2f}")
    print(f"[green]Decimals:[/green] {decimals}")
    return total_supply


def estimate_price(mint: Pubkey):
    # Ambil akun terbesar — biasanya akun liquidity pool
    largest = client.get_token_largest_accounts(mint)

    if not largest.value:
        print("[red]Tidak ditemukan akun terbesar (mungkin token tidak aktif).[/red]")
        return None

    # Ambil satu akun terbesar
    token_account = largest.value[0].address

    # Ambil saldo dari akun tersebut
    balance_resp = client.get_token_account_balance(token_account)
    if not balance_resp.value:
        print("[red]Gagal ambil saldo token.[/red]")
        return None

    ui_amount = float(balance_resp.value.ui_amount_string or 0)
    if ui_amount == 0:
        print("[red]Saldo token nol, tidak bisa hitung harga.[/red]")
        return None

    # Asumsi akun ini adalah liquidity pool SOL-token
    # Ambil balance SOL dari akun pool
    sol_account_info = client.get_balance(token_account)
    sol_balance = int(sol_account_info.value) / 1e9  # lamports -> SOL

    if sol_balance == 0:
        print("[red]Saldo SOL di akun ini nol, bukan pool?[/red]")
        return None

    # Estimasi harga token (SOL/token)
    price = sol_balance / ui_amount
    print(f"[cyan]Estimasi Harga Token:[/cyan] {price:.10f} SOL")
    return price


def get_holders_count(mint: Pubkey):
    resp = client.get_token_largest_accounts(mint)
    if not resp.value:
        return 0
    return len(resp.value)


def check_100x_potential(supply, price, holders, liquidity=3):
    market_cap = supply * price
    print(f"[magenta]Estimasi Market Cap:[/magenta] {market_cap:.4f} SOL")
    print(f"[magenta]Holders Dikenali:[/magenta] {holders}")

    if market_cap > 10:
        return False, "Market cap terlalu besar"
    if holders < 100:
        return False, "Jumlah holder terlalu sedikit"
    if liquidity < 2:
        return False, "Likuiditas terlalu kecil"

    return True, "Potensi 100x: microcap + distribusi awal oke"


def analyze_token(mint: Pubkey):
    print(f"[bold blue]Analisa Token:[/bold blue] {mint}")
    supply = get_token_info(mint)
    if supply is None:
        return

    price = estimate_price(mint)
    if price is None:
        return

    holders = get_holders_count(mint)
    is_potential, reason = check_100x_potential(supply, price, holders)

    if is_potential:
        print(f"[bold green]✅ POTENSI 100x![/bold green] — {reason}")
    else:
        print(f"[bold yellow]⚠️ Tidak cocok 100x:[/bold yellow] {reason}")


# Jalankan analisa
analyze_token(mint_address)
