import socket
import json
import time
from web3 import Web3

# =========================
# CONFIG
# =========================

RPC_URL = "https://mainnet.infura.io/v3/TU_API_KEY"
CONTRACT_ADDRESS = "0xTU_CONTRATO"
SIGNER_HOST = "127.0.0.1"
SIGNER_PORT = 5000

# ABI minimo (solo funciones usadas)
ABI = [
    {
        "inputs":[{"internalType":"uint256","name":"i","type":"uint256"},
                  {"internalType":"uint256","name":"j","type":"uint256"},
                  {"internalType":"int256","name":"valor","type":"int256"}],
        "name":"escribirRelacion",
        "outputs":[],
        "stateMutability":"nonpayable",
        "type":"function"
    },
    {
        "inputs":[{"internalType":"string","name":"nota","type":"string"},
                  {"internalType":"int256","name":"intensidad","type":"int256"}],
        "name":"registrarEstado",
        "outputs":[],
        "stateMutability":"nonpayable",
        "type":"function"
    }
]

# =========================
# WEB3
# =========================

w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# direccion dummy (solo para construir tx)
# la real la conoce el signer
FROM_ADDRESS = "0x0000000000000000000000000000000000000000"

# =========================
# SIGNER CLIENT
# =========================

def solicitar_firma(tx):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SIGNER_HOST, SIGNER_PORT))

    client.send(json.dumps(tx).encode())

    response = client.recv(8192).decode()
    client.close()

    if response.startswith("ERROR"):
        raise Exception(response)

    return response

# =========================
# BUILD TX
# =========================

def build_tx(tx_data, nonce):

    return {
        "to": tx_data["to"],
        "data": tx_data["data"],
        "gas": 200000,
        "gasPrice": w3.to_wei("10", "gwei"),
        "nonce": nonce,
        "chainId": 1,  # mainnet (cambiar si testnet)
        "value": 0
    }

# =========================
# ENVIO A BLOCKCHAIN
# =========================

def enviar_tx(raw_tx):

    tx_hash = w3.eth.send_raw_transaction(bytes.fromhex(raw_tx[2:]))
    return tx_hash.hex()

# =========================
# LOGICA TAPIZ (MINIMA)
# =========================

def generar_estado():

    # placeholder simple (reemplazar por tu eigen real)
    i = int(time.time()) % 3
    j = (i + 1) % 3
    intensidad = (i - j) * 10

    return i, j, intensidad

# =========================
# LOOP PRINCIPAL
# =========================

def loop():

    nonce = w3.eth.get_transaction_count(FROM_ADDRESS)

    while True:

        try:
            i, j, intensidad = generar_estado()

            # --- tx 1: escribirRelacion ---
            tx1_data = contract.functions.escribirRelacion(
                i, j, int(intensidad)
            ).build_transaction({"from": FROM_ADDRESS})

            tx1 = build_tx(tx1_data, nonce)

            firma1 = solicitar_firma(tx1)
            hash1 = enviar_tx(firma1)

            print("Relacion tx:", hash1)

            nonce += 1

            # --- tx 2: registrarEstado ---
            nota = f"{i}->{j}"

            tx2_data = contract.functions.registrarEstado(
                nota, int(intensidad)
            ).build_transaction({"from": FROM_ADDRESS})

            tx2 = build_tx(tx2_data, nonce)

            firma2 = solicitar_firma(tx2)
            hash2 = enviar_tx(firma2)

            print("Estado tx:", hash2)

            nonce += 1

        except Exception as e:
            print("ERROR:", e)

        time.sleep(10)

# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    loop()