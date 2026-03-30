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

def loop():

    from_addr = get_address()
    print("Signer address:", from_addr)

    while True:

        try:
            nonce = get_nonce()

            i, j, intensidad = generar_estado()

            # tx1
            tx1 = contract.functions.escribirRelacion(
                i, j, int(intensidad)
            ).build_transaction({
                "from": from_addr,
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": w3.to_wei("10", "gwei"),
                "chainId": 1
            })

            raw1 = sign_tx(tx1)
            hash1 = w3.eth.send_raw_transaction(bytes.fromhex(raw1[2:]))
            print("tx1:", hash1.hex())

            # tx2
            tx2 = contract.functions.registrarEstado(
                f"{i}->{j}", int(intensidad)
            ).build_transaction({
                "from": from_addr,
                "nonce": nonce + 1,
                "gas": 200000,
                "gasPrice": w3.to_wei("10", "gwei"),
                "chainId": 1
            })

            raw2 = sign_tx(tx2)
            hash2 = w3.eth.send_raw_transaction(bytes.fromhex(raw2[2:]))
            print("tx2:", hash2.hex())

        except Exception as e:
            print("ERROR:", e)

        time.sleep(10)

if __name__ == "__main__":
    loop()