import ccxt
import pandas as pd
import requests
import time

from datetime import datetime


TOKEN = "8344667920:AAHlOLGTJOidhK7cGj9kDVFYVfZG_j-H-s8"
CHAT_ID = "8326776188"


exchange = ccxt.binance()


pares = [

"BTC/USDT",
"ETH/USDT",
"BNB/USDT",
"SOL/USDT",
"XRP/USDT",
"ADA/USDT",
"AVAX/USDT",
"DOGE/USDT",
"LINK/USDT",
"LTC/USDT",
"DOT/USDT",
"TRX/USDT",
"ATOM/USDT",
"FIL/USDT",
"TON/USDT"

]


def analisar(df):

    df["m9"] = df["close"].rolling(9).mean()
    df["m21"] = df["close"].rolling(21).mean()

    delta = df["close"].diff()

    ganho = delta.clip(lower=0).rolling(14).mean()
    perda = -delta.clip(upper=0).rolling(14).mean()

    rs = ganho/perda

    df["RSI"] = 100-(100/(1+rs))

    df = df.dropna()

    if len(df) < 30:
        return None


    ultima = df.iloc[-1]

    preco = float(ultima["close"])
    rsi = float(ultima["RSI"])

    score = 0


    if ultima["m9"] > ultima["m21"]:
        score += 2
        direcao="🚀 COMPRA"
    else:
        score += 2
        direcao="⚠️ VENDA"


    if rsi > 60:
        score += 2

    if rsi < 40:
        score += 2


    media_volume = df["volume"].rolling(20).mean().iloc[-1]
    volume_atual = df["volume"].iloc[-1]

    explosao = volume_atual > media_volume*1.8

    if explosao:
        score += 3


    return score,direcao,preco,rsi,explosao


while True:

    ranking=[]

    for par in pares:

        try:

            velas = exchange.fetch_ohlcv(par,"5m",limit=120)

            df = pd.DataFrame(
                velas,
                columns=["t","open","high","low","close","volume"]
            )

            resultado = analisar(df)

            if resultado is None:
                continue

            score,direcao,preco,rsi,explosao = resultado

            ranking.append((score,par,direcao,preco,rsi,explosao))

        except:

            continue


    if len(ranking)==0:

        print("Sem oportunidades")

        time.sleep(60)

        continue


    ranking.sort(reverse=True)

    melhor = ranking[0]

    score,par,direcao,preco,rsi,explosao = melhor


    if score < 6:

        print("Nenhum sinal forte")

        time.sleep(60)

        continue


    alerta=""

    if explosao:
        alerta="⚡ Volume explosivo"


    agora=datetime.now().strftime("%H:%M:%S")


    msg=f"""
🥷 RADAR IA NINJA | KADU

{direcao}

Par: {par}

Score: {score}

RSI: {round(rsi,2)}
Preço: {round(preco,4)}

{alerta}

Horário: {agora}
"""


    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id":CHAT_ID,
            "text":msg
        }
    )


    print("Sinal enviado")

    time.sleep(300)
