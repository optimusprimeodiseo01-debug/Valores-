import socket
import json
from web3 import Web3
import time

HOST = "127.0.0.1"
PORT = 5000

KEY_FILE = "infra/key.txt"

MAX_GAS = 300000
MAX_VALUE_ETH = 0.05
RATE_LIMIT_SECONDS = 2

RPC_URL = "https://mainnet.infura.io/v3/TU_API_KEY"

# =========================
# INIT
# =========================

with open(KEY_FILE) as f:
    PRIVATE_KEY = f.read().strip()

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

last_signature_time = 0

# =========================
# HELPERS
# =========================

def get_address():
    return account.address

def get_nonce():
    return w3.eth.get_transaction_count(account.address)

def validar_tx(tx):

    if "to" not in tx:
        raise Exception("tx sin destino")

    if "gas" not in tx:
        raise Exception("tx sin gas")

    if int(tx["gas"]) > MAX_GAS:
        raise Exception("gas excedido")

    if "value" in tx:
        if int(tx["value"]) > Web3.to_wei(MAX_VALUE_ETH, "ether"):
            raise Exception("valor excedido")

# =========================
# SIGN
# =========================

def firmar_tx(tx):

    global last_signature_time

    now = time.time()
    if now - last_signature_time < RATE_LIMIT_SECONDS:
        raise Exception("rate limit")

    validar_tx(tx)

    signed = account.sign_transaction(tx)
    last_signature_time = now

    return signed.rawTransaction.hex()

# =========================
# SERVER
# =========================

def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[Signer] activo {HOST}:{PORT}")

    while True:

        conn, _ = server.accept()

        try:
            data = conn.recv(8192).decode()

            if not data:
                conn.close()
                continue

            req = json.loads(data)

            cmd = req.get("cmd")

            if cmd == "get_address":
                response = get_address()

            elif cmd == "get_nonce":
                response = get_nonce()

            elif cmd == "sign":
                tx = req.get("tx")
                response = firmar_tx(tx)

            else:
                response = "ERROR: cmd desconocido"

            conn.send(str(response).encode())

        except Exception as e:
            conn.send(f"ERROR: {str(e)}".encode())

        finally:
            conn.close()

if __name__ == "__main__":
    start_server()