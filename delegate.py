import httpx
import base64
import hashlib
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigencode_string
from google.protobuf import any_pb2
from google.protobuf.json_format import MessageToDict
from cosmospy_protobuf.cosmos.tx.v1beta1 import tx_pb2
from cosmospy_protobuf.cosmos.crypto.secp256k1 import keys_pb2
from cosmospy_protobuf.cosmos.staking.v1beta1 import tx_pb2 as staking_tx_pb2
from cosmospy_protobuf.cosmos.base.v1beta1 import coin_pb2

API_URL = "https://lcd-initia-testnet.keplr.app"
CHAIN_ID = "initiation-1"

def get_account_info(address):
    url = f"{API_URL}/cosmos/auth/v1beta1/accounts/{address}"
    response = httpx.get(url, verify=False)
    if response.status_code == 200:
        account_data = response.json().get('account', {})
        return {
            "account_number": int(account_data.get('account_number', 0)),
            "sequence": int(account_data.get('sequence', 0)),
            "pub_key": account_data.get('pub_key', {}).get('key', '')
        }
    else:
        print("Failed to fetch account info:", response.status_code)
        return None

def sign_transaction(sign_doc_bytes, private_key):
    sha256_hash = hashlib.sha256(sign_doc_bytes).digest()
    signing_key = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
    signature = signing_key.sign_digest(sha256_hash, sigencode=sigencode_string)
    return signature

def create_signed_delegate_tx(private_key, delegator_address, validator_address, amount, account_number, sequence):
    print("Creating MsgDelegate...")
    # MsgDelegate
    msg_delegate = staking_tx_pb2.MsgDelegate()
    msg_delegate.delegator_address = delegator_address
    msg_delegate.validator_address = validator_address
    amount_coin = coin_pb2.Coin()
    amount_coin.denom = "uinit"
    amount_coin.amount = str(amount)
    msg_delegate.amount.CopyFrom(amount_coin)

    print("Creating TxBody...")
    # TxBody
    tx_body = tx_pb2.TxBody()
    any_msg_delegate = any_pb2.Any()
    any_msg_delegate.Pack(msg_delegate)
    any_msg_delegate.type_url = "/initia.mstaking.v1.MsgDelegate"  # Bu kısmı doğru tür URL'si ile güncelliyoruz
    tx_body.messages.append(any_msg_delegate)
    tx_body.memo = ""

    # AuthInfo
    print("Fetching account info...")
    pub_key_base64 = get_account_info(delegator_address)["pub_key"]
    pub_key_bytes = base64.b64decode(pub_key_base64)
    pub_key = keys_pb2.PubKey(key=pub_key_bytes)

    any_pub_key = any_pb2.Any()
    any_pub_key.Pack(pub_key)
    any_pub_key.type_url = "/cosmos.crypto.secp256k1.PubKey"

    fee = tx_pb2.Fee()
    fee.amount.add(denom="move/944f8dd8dc49f96c25fea9849f16436dcfa6d564eec802f3ef7f8b3ea85368ff", amount="122942")
    fee.gas_limit = 409805

    signer_info = tx_pb2.SignerInfo()
    single = tx_pb2.ModeInfo.Single()
    single.mode = 1  # SIGN_MODE_DIRECT
    signer_info.mode_info.single.CopyFrom(single)
    signer_info.sequence = sequence
    signer_info.public_key.CopyFrom(any_pub_key)

    auth_info = tx_pb2.AuthInfo()
    auth_info.signer_infos.append(signer_info)
    auth_info.fee.CopyFrom(fee)

    print("Creating SignDoc...")
    # SignDoc
    sign_doc = tx_pb2.SignDoc()
    sign_doc.body_bytes = tx_body.SerializeToString()
    sign_doc.auth_info_bytes = auth_info.SerializeToString()
    sign_doc.chain_id = CHAIN_ID
    sign_doc.account_number = account_number

    sign_doc_bytes = sign_doc.SerializeToString()
    signature = sign_transaction(sign_doc_bytes, private_key)

    print("Creating Tx...")
    # Tx
    tx = tx_pb2.Tx()
    tx.body.CopyFrom(tx_body)
    tx.auth_info.CopyFrom(auth_info)
    tx.signatures.append(signature)

    return tx

def broadcast_tx(tx):
    print("Broadcasting Tx...")
    tx_bytes = tx.SerializeToString()
    push_url = f"{API_URL}/cosmos/tx/v1beta1/txs"
    data = {"tx_bytes": base64.b64encode(tx_bytes).decode(), "mode": "BROADCAST_MODE_SYNC"}
    response = httpx.post(push_url, json=data, headers={'Content-Type': 'application/json'}, verify=False)
    return response.json()

def delegate_to_validator(private_key, delegator_address, validator_address, amount):
    print("Fetching account info for delegation...")
    account_info = get_account_info(delegator_address)
    if not account_info:
        return False

    account_number = account_info["account_number"]
    sequence = account_info["sequence"]

    print("Creating signed transaction for delegation...")
    tx = create_signed_delegate_tx(private_key, delegator_address, validator_address, amount, account_number, sequence)
    response = broadcast_tx(tx)

    print(response)
    return response
