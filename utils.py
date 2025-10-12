import requests

TOTAL_TOKENS = 5_000_000_000
AIRDROP_RATIO = 0.05
XP_TOKEN_RATIO = 0.16
PRESALE_RATIO = 0.03
P1_SYMBOL = 'play_solana'
P2_SYMBOL = 'player2_'
PSG_SYMBOL = 'psg1_genesis'


def get_nft_xp(p1_num: int, p2_num: int):
    return p1_num * 10_000 + p2_num * 5_000


def get_collection_unique_holders(symbol: str) -> int:
    url = f"https://api-mainnet.magiceden.dev/v2/collections/{symbol}/holder_stats"
    resp = requests.get(url)
    data = resp.json()
    return data['uniqueHolders']


def get_collection_supply(symbol: str) -> int:
    url = f"https://api-mainnet.magiceden.dev/v2/collections/{symbol}/holder_stats"
    resp = requests.get(url)
    data = resp.json()
    return data['totalSupply']


def get_coll_stat(symbol: str) -> tuple[int, int]:
    uniq_holders = get_collection_unique_holders(symbol)
    supply = get_collection_supply(symbol)

    return uniq_holders, supply


def get_total_playdex_stat() -> tuple[int, list, list]:
    url = "https://www.playsolana.com/api/leaderboard?page=1&limit=22000"  # можно увеличить лимит

    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "Referer": "https://www.playsolana.com/playdex/leaderboard",
    }
    cookies = {
        # Если leaderboard публичный, можно оставить пусто {}
        # Если нужен авторизованный доступ — добавь свои куки:
        # "access_token": "U2FsdGVkX18ZXv...",
        # "refresh_token": "U2FsdGVkX1%2BJ%2FUI..."
    }
    response = requests.get(url, headers=headers, cookies=cookies)
    data = response.json()
    sum_points = 0
    points = []
    names = []
    for user in data['leaderboard']:
        sum_points += user['totalScore']
        points.append(user['totalScore'])
        names.append(user['name'])

    return sum_points, dict(zip(names, points))


def prepare_user_col_stats(wallet_address: str) -> tuple[int, int]:
    url = f"https://api-mainnet.magiceden.dev/v2/wallets/{wallet_address}/tokens"
    resp = requests.get(url)
    data = resp.json()
    token_cols = [x['collection'] for x in data]
    p1_count = len([x for x in token_cols if x == P1_SYMBOL])
    p2_count = len([x for x in token_cols if x == P2_SYMBOL])
    psg_count = len([x for x in token_cols if x == PSG_SYMBOL])

    return p1_count, p2_count, psg_count


def calculate_tokens(wallet_address: str, playdex_name: str) -> float:

    # COLLECTIONS STAT
    p2_holders, p2_total = get_coll_stat(symbol=P2_SYMBOL)
    p1_holders, p1_total = get_coll_stat(symbol=P1_SYMBOL)
    psg_holders = get_collection_unique_holders(symbol=PSG_SYMBOL)
    total_nft_xp = get_nft_xp(p1_num=p1_total, p2_num=p2_total)
    total_playdex_xp, users_xp_dict = get_total_playdex_stat()
    total_xp = total_nft_xp + total_playdex_xp

    # TOKENS STAT
    airdrop_tokens = int(AIRDROP_RATIO * TOTAL_TOKENS)
    xp_tokens = int(XP_TOKEN_RATIO * TOTAL_TOKENS)

    # USER STAT
    user_p1, user_p2, user_psg = prepare_user_col_stats(
        wallet_address=wallet_address
    )
    user_nft_xp = get_nft_xp(p1_num=user_p1, p2_num=user_p2)
    user_playdex_xp = users_xp_dict.get(playdex_name, 0)
    total_user_xp = user_nft_xp + user_playdex_xp

    airdrop_pts = user_psg / psg_holders * airdrop_tokens
    xp_pts = total_user_xp / total_xp * xp_tokens
    return {
        'airdrop_tokens': airdrop_pts,
        'xp_tokens': xp_pts,
        'total_tokens': airdrop_pts + xp_pts
    }
