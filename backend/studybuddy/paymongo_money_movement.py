import base64
import decimal

import requests
from django.conf import settings


PAYMONGO_API_BASE_URL = 'https://api.paymongo.com/v1'

# Every Studybuddy cash-out moves through InstaPay (see ADR-0001) -- PESONet is no
# longer a reachable code path.
INSTAPAY_PROVIDER = 'instapay'


class PayMongoCashOutError(Exception):
    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body or {}


def get_money_movement_headers():
    token = base64.b64encode(f"{settings.PAYMONGO_SECRET_KEY}:".encode()).decode()
    return {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def get_paymongo_error_detail(response_body):
    errors = response_body.get('errors') if isinstance(response_body, dict) else None
    if isinstance(errors, list) and errors:
        first_error = errors[0] or {}
        return (
            first_error.get('detail')
            or first_error.get('message')
            or first_error.get('code')
            or 'PayMongo rejected the cash-out request.'
        )

    return 'PayMongo rejected the cash-out request.'


def parse_decimal(value, default='0.00'):
    if value in (None, ''):
        return decimal.Decimal(default)

    return decimal.Decimal(str(value))


def normalize_wallet_transaction(response_body):
    data = response_body.get('data') or {}
    attributes = data.get('attributes') or {}
    provider_error = attributes.get('provider_error') or ''

    return {
        'id': data.get('id') or '',
        'status': attributes.get('status') or data.get('status') or '',
        'provider': attributes.get('provider') or '',
        'reference_number': attributes.get('reference_number') or '',
        'provider_error_code': attributes.get('provider_error_code') or '',
        'provider_error_message': (
            provider_error.get('detail')
            if isinstance(provider_error, dict)
            else str(provider_error or '')
        ),
        'fee': parse_decimal(attributes.get('fee')),
        'net_amount': parse_decimal(attributes.get('net_amount')),
        'raw': response_body,
    }


def list_receiving_institutions():
    response = requests.get(
        f'{PAYMONGO_API_BASE_URL}/wallets/receiving_institutions',
        params={'provider': INSTAPAY_PROVIDER},
        headers=get_money_movement_headers(),
    )

    try:
        response_body = response.json()
    except ValueError:
        response_body = {'raw': getattr(response, 'text', '')}

    if response.status_code != 200:
        raise PayMongoCashOutError(
            get_paymongo_error_detail(response_body),
            status_code=response.status_code,
            response_body=response_body,
        )

    return response_body


def create_wallet_transaction(wallet_id, payout_account, amount, callback_url, withdrawal_id):
    if getattr(settings, 'PAYMONGO_CASHOUT_MOCK', False):
        return {
            'id': f'mock_wtx_{withdrawal_id}',
            'status': 'succeeded',
            'provider': INSTAPAY_PROVIDER,
            'reference_number': f'MOCK-{withdrawal_id}',
            'provider_error_code': '',
            'provider_error_message': '',
            'fee': decimal.Decimal('0.00'),
            'net_amount': parse_decimal(amount),
            'raw': {'mock': True},
        }

    if not wallet_id:
        raise PayMongoCashOutError('PayMongo wallet is not configured.')

    attributes = {
        'amount': str(amount),
        'currency': 'PHP',
        'description': f'StudyBuddy tutor cash-out #{withdrawal_id}',
        'purpose': 'Tutor cash-out',
        'provider': INSTAPAY_PROVIDER,
        'receiver': {
            'bank_id': payout_account.receiving_institution_id,
            'bank_code': payout_account.receiving_institution_code,
            'bank_name': payout_account.receiving_institution_name,
            'bank_account_number': payout_account.account_number,
            'bank_account_name': payout_account.account_name,
        },
    }

    if callback_url:
        attributes['callback_url'] = callback_url

    response = requests.post(
        f'{PAYMONGO_API_BASE_URL}/wallets/{wallet_id}/transactions',
        json={'data': {'attributes': attributes}},
        headers=get_money_movement_headers(),
    )

    try:
        response_body = response.json()
    except ValueError:
        response_body = {'raw': getattr(response, 'text', '')}

    if response.status_code not in (200, 201):
        raise PayMongoCashOutError(
            get_paymongo_error_detail(response_body),
            status_code=response.status_code,
            response_body=response_body,
        )

    return normalize_wallet_transaction(response_body)
