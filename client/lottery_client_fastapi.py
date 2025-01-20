import os

from fastapi import FastAPI
from web3 import Web3
from dotenv import load_dotenv
from web3.datastructures import AttributeDict
from hexbytes import HexBytes

# Загрузка переменных окружения
load_dotenv()

app = FastAPI()

RPC_URL = "http://127.0.0.1:8545"  # адрес JSON-RPC локальной сети (поднимается вместе с Hardhat)
w3 = Web3(Web3.HTTPProvider(RPC_URL))

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY not found in .env")

# Адрес аккаунта
account = w3.eth.account.from_key(PRIVATE_KEY)
OWNER_ADDRESS = account.address

# ABI (Lottery.sol)
ABI = [
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_durationMinutes",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_ticketPrice",
                "type": "uint256"
            }
        ],
        "stateMutability": "payable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "winner",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "WinnerSelected",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "getContractBalance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getPlayersCount",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getRandomNumber",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "lotteryEndTime",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "manager",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "participate",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "name": "players",
        "outputs": [
            {
                "internalType": "address payable",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "selectWinner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "ticketPrice",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Адрес контракта (из вывода Hardhat)
RAW_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
CONTRACT_ADDRESS = Web3.to_checksum_address(RAW_ADDRESS)

# Создаём экземпляр контракта
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)


def convert_bytes_and_attrs(obj):
    """Рекурсивно обходит структуру (dict, list, AttributeDict) для вывода информации и:
      - Байты (bytes, HexBytes) конвертирует в hex-строки.
      - AttributeDict приводит к dict, затем обходит дальше.
    """
    if isinstance(obj, HexBytes):  # web3 использует HexBytes
        return obj.hex()

    if isinstance(obj, (bytes, bytearray)):
        return obj.hex()

    if isinstance(obj, AttributeDict):
        # Сначала делаем обычный dict, потом обрабатываем его
        return {k: convert_bytes_and_attrs(v) for k, v in dict(obj).items()}

    if isinstance(obj, dict):
        return {k: convert_bytes_and_attrs(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [convert_bytes_and_attrs(item) for item in obj]

    # Для всего остального (int, str, None...) ничего не делаем
    return obj


def send_transaction(func, value=0):
    """Функция для отправки транзакции и получения receipt.

    func  - объект вида contract.functions.someMethod(...).
    value - сколько wei пересылать (по умолчанию 0).
    """
    nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
    tx = func.build_transaction({
        'from': OWNER_ADDRESS,
        'nonce': nonce,
        'value': value,
        # 'gas': 3_000_000,  можно задать, можно не задавать
        # 'gasPrice': w3.toWei('10', 'gwei')
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    raw_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    receipt_dict = dict(raw_receipt)  # Превращаем receipt в JSON-friendly словарь
    return convert_bytes_and_attrs(receipt_dict)


@app.get("/")
def index():
    return {"message": "Lottery Client. Доступные эндпоинты: /manager, /participate, /selectWinner, ..."}


@app.get("/manager")
def get_manager():
    return {"manager": contract.functions.manager().call()}


@app.get("/ticketPrice")
def get_ticket_price():
    return {"ticketPrice": str(contract.functions.ticketPrice().call())}


@app.get("/lotteryEndTime")
def get_lottery_end_time():
    return {"lotteryEndTime": contract.functions.lotteryEndTime().call()}


@app.get("/getRandomNumber")
def get_random_number():
    return {"randomNumber": str(contract.functions.getRandomNumber().call())}


@app.get("/getPlayersCount")
def get_players_count():
    return {"playersCount": contract.functions.getPlayersCount().call()}


@app.get("/getContractBalance")
def get_contract_balance():
    balance = contract.functions.getContractBalance().call()
    return {"contractBalance": str(balance)}


@app.get("/player/{idx}")
def get_player_by_index(idx: int):
    """Возвращает адрес игрока по индексу(Пример: 0-10)."""
    player_addr = contract.functions.players(idx).call()
    return {"playerAddress": player_addr}


@app.post("/participate")
def participate():
    """Отправляет транзакцию participate() c value = ticketPrice.

    Если в контракте лотерея уже окончена, вернётся ошибка от контракта.
    """
    price = contract.functions.ticketPrice().call()

    # Можно дополнительно проверить текущее время против lotteryEndTime:
    current_block = w3.eth.get_block('latest')
    current_time = current_block['timestamp']
    end_time = contract.functions.lotteryEndTime().call()

    if current_time >= end_time:
        return {
            "status": "error",
            "message": f"Lottery ended at {end_time}, now {current_time}"
        }

    receipt = send_transaction(contract.functions.participate(), value=price)
    return {"status": "participated", "txReceipt": receipt}


@app.post("/selectWinner")
def select_winner():
    # Проверяем, что вызывающий - это менеджер
    manager_addr = contract.functions.manager().call()
    if manager_addr.lower() != OWNER_ADDRESS.lower():
        return {
            "status": "error",
            "message": "Only manager can call this function."
        }

    # Проверяем, что лотерея окончилась
    current_block = w3.eth.get_block('latest')
    current_time = current_block['timestamp']
    end_time = contract.functions.lotteryEndTime().call()

    if current_time < end_time:
        return {
            "status": "error",
            "message": "Lottery has not ended yet (no winner can be selected).",
            "currentTime": current_time,
            "endTime": end_time
        }

    # Отправляем транзакцию
    receipt = send_transaction(contract.functions.selectWinner())
    return {
        "status": "winner selected",
        "txReceipt": receipt,
    }
