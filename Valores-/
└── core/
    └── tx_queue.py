import time
import json
import socket
from web3 import Web3

# =========================
# CONFIG
# =========================

SIGNER_HOST = "127.0.0.1"
SIGNER_PORT = 5000

RPC_URL = "https://mainnet.infura.io/v3/TU_API_KEY"

RETRY_LIMIT = 3
PENDING_TIMEOUT = 60  # segundos

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# =========================
# SIGNER CLIENT
# =========================

def call_signer(payload):
    s = socket.socket()
    s.connect((SIGNER_HOST, SIGNER_PORT))
    s.send(json.dumps(payload).encode())
    res = s.recv(8192).decode()
    s.close()

    if res.startswith("ERROR"):
        raise Exception(res)

    return res

def get_address():
    return call_signer({"cmd": "get_address"})

def get_nonce():
    return int(call_signer({"cmd": "get_nonce"}))

def sign_tx(tx):
    return call_signer({"cmd": "sign", "tx": tx})

# =========================
# TX QUEUE
# =========================

class TxQueue:

    def __init__(self):
        self.queue = []
        self.pending = {}

    def add(self, tx_builder):
        self.queue.append({
            "builder": tx_builder,
            "retries": 0
        })

    def process(self):

        if not self.queue:
            return

        from_addr = get_address()
        nonce = get_nonce()

        next_queue = []

        for item in self.queue:

            try:
                tx = item["builder"](from_addr, nonce)

                raw = sign_tx(tx)
                tx_hash = w3.eth.send_raw_transaction(bytes.fromhex(raw[2:]))

                h = tx_hash.hex()

                print("ENVIADA:", h)

                self.pending[h] = {
                    "timestamp": time.time(),
                    "tx": tx
                }

                nonce += 1

            except Exception as e:
                print("ERROR TX:", e)

                item["retries"] += 1

                if item["retries"] < RETRY_LIMIT:
                    next_queue.append(item)
                else:
                    print("DESCARTADA")

        self.queue = next_queue

    def check_pending(self):

        to_remove = []

        for h, data in self.pending.items():

            try:
                receipt = w3.eth.get_transaction_receipt(h)

                if receipt:
                    print("CONFIRMADA:", h)
                    to_remove.append(h)

            except:
                pass

            # timeout
            if time.time() - data["timestamp"] > PENDING_TIMEOUT:
                print("TIMEOUT:", h)
                to_remove.append(h)

        for h in to_remove:
            del self.pending[h]