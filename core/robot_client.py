import socket
import json
import time
from web3 import Web3

RPC_URL = "https://mainnet.infura.io/v3/TU_API_KEY"
CONTRACT_ADDRESS = "0xTU_CONTRATO"

SIGNER_HOST = "127.0.0.1"
SIGNER_PORT = 5000

w3 = Web3(Web3.HTTPProvider(RPC_URL))

ABI = [
    {
        "inputs":[{"name":"i","type":"uint256"},
                  {"name":"j","type":"uint256"},
                  {"name":"valor","type":"int256"}],
        "name":"escribirRelacion",
        "outputs":[],
        "stateMutability":"nonpayable",
        "type":"function"
    },
    {
        "inputs":[{"name":"nota","type":"string"},
                  {"name":"intensidad","type":"int256"}],
        "name":"registrarEstado",
        "outputs":[],
        "stateMutability":"nonpayable",
        "type":"function"
    }
]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

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
# LOGICA TAPIZ
# =========================

def generar_estado():
    t = int(time.time())
    i = t % 3
    j = (i + 1) % 3
    intensidad = (i - j) * 10
    return i, j, intensidad

# =========================
# LOOP
# =========================

from tx_queue import TxQueue

queue = TxQueue()

def loop():

    from_addr = get_address()
    print("Signer:", from_addr)

    while True:

        try:
            i, j, intensidad = generar_estado()

            # builder tx1
            def tx1_builder(addr, nonce):
                return contract.functions.escribirRelacion(
                    i, j, int(intensidad)
                ).build_transaction({
                    "from": addr,
                    "nonce": nonce,
                    "gas": 200000,
                    "gasPrice": w3.to_wei("10", "gwei"),
                    "chainId": 1
                })

            # builder tx2
            def tx2_builder(addr, nonce):
                return contract.functions.registrarEstado(
                    f"{i}->{j}", int(intensidad)
                ).build_transaction({
                    "from": addr,
                    "nonce": nonce,
                    "gas": 200000,
                    "gasPrice": w3.to_wei("10", "gwei"),
                    "chainId": 1
                })

            queue.add(tx1_builder)
            queue.add(tx2_builder)

            queue.process()
            queue.check_pending()

        except Exception as e:
            print("ERROR LOOP:", e)

        time.sleep(5)