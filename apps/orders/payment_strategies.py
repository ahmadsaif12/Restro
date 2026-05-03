# orders/payment_strategies.py
from django.conf import settings
from .utils import generate_esewa_signature


class EsewaStrategy:
    """
    eSewa uses a form-submission model.
    We build hidden form fields — frontend submits the form directly to eSewa.
    """

    def get_payment_payload(self, order):
        conf = settings.ESEWA_SETTINGS

        # "100" vs "100.00" produce DIFFERENT signatures — always use .2f
        amount_str = "{:.2f}".format(order.total_amount)

        signature = generate_esewa_signature(
            total_amount=amount_str,
            transaction_uuid=order.order_code,
            product_code=conf["MERCHANT_ID"],
            secret_key=conf["SECRET_KEY"]
        )

        return {
            "payment_method": "eSewa",
            "esewa_payload": {
                "amount": amount_str,
                "tax_amount": "0",
                "total_amount": amount_str,
                "product_service_charge": "0",
                "product_delivery_charge": "0",
                "transaction_uuid": order.order_code,
                "product_code": conf["MERCHANT_ID"],
                "success_url": conf["SUCCESS_URL"],
                "failure_url": conf["FAILURE_URL"],
                "signed_field_names": "total_amount,transaction_uuid,product_code",
                "signature": signature,
                "esewa_url": conf["INITIATE_URL"]
            }
        }


class KhaltiStrategy:
    """
    Khalti uses a server-side API call model.
    We call Khalti's API → get a payment URL → redirect user there.
    """

    def get_payment_payload(self, order):
        conf = settings.KHALTI_SETTINGS

        return {
            "payment_method": "Khalti",
            "khalti_payload": {
                "return_url": conf["SUCCESS_URL"],
                "website_url": conf["WEBSITE_URL"],
                "amount": int(order.total_amount * 100),  # Khalti uses paisa (×100)
                "purchase_order_id": order.order_code,
                "purchase_order_name": f"Order ORD-{order.order_code}",
                "merchant_secret": conf["SECRET_KEY"],
                "khalti_url": conf["INITIATE_URL"]
            }
        }


class CODStrategy:
    """
    Cash on Delivery — no external gateway needed.
    Just mark payment as pending and confirm the order.
    """

    def get_payment_payload(self, order):
        return {
            "payment_method": "COD",
            "cod_payload": {
                "message": "Order confirmed. Pay at the table.",
                "order_code": order.order_code,
            }
        }


# Registry — maps payment_method string to its strategy class
PAYMENT_STRATEGIES = {
    "eSewa": EsewaStrategy,
    "Khalti": KhaltiStrategy,
    "COD": CODStrategy,
}


def get_payment_strategy(payment_method):
    """
    Factory function — call this in views.py.
    
    Usage:
        strategy = get_payment_strategy(order.payment_method)
        payload = strategy.get_payment_payload(order)
    """
    strategy_class = PAYMENT_STRATEGIES.get(payment_method)
    if not strategy_class:
        raise ValueError(f"Unsupported payment method: {payment_method}")
    return strategy_class()