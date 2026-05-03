# orders/utils.py
import hmac
import hashlib
import base64


def generate_esewa_signature(total_amount, transaction_uuid, product_code, secret_key):
    """
    Generate HMAC-SHA256 signature for eSewa epay v2.

    CRITICAL FORMAT RULES:
    - Fields separated by commas with NO spaces
    - Exact order: total_amount, transaction_uuid, product_code
    - Each field in key=value format
    - Output is Base64-encoded (not hex)
    """
    data = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"

    secret_key_bytes = secret_key.encode('utf-8')
    data_bytes = data.encode('utf-8')

    signature = hmac.new(secret_key_bytes, data_bytes, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')


def verify_esewa_signature(response_data, secret_key):
    """
    Verify the signature returned by eSewa after payment.
    Call this in your success callback view to confirm the response is genuine.
    """
    received_signature = response_data.get('signature')
    total_amount = response_data.get('total_amount')
    transaction_uuid = response_data.get('transaction_uuid')
    product_code = response_data.get('product_code')

    if not all([received_signature, total_amount, transaction_uuid, product_code]):
        return False

    expected_signature = generate_esewa_signature(
        total_amount, transaction_uuid, product_code, secret_key
    )
    return hmac.compare_digest(received_signature, expected_signature)