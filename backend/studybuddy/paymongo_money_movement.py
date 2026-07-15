import base64
import decimal

import requests
from django.conf import settings


PAYMONGO_API_BASE_URL = 'https://api.paymongo.com/v1'
PAYMONGO_REQUEST_TIMEOUT = 20

# Every Studybuddy cash-out moves through InstaPay (see ADR-0001) -- PESONet is no
# longer a reachable code path.
INSTAPAY_PROVIDER = 'instapay'

# Dev-only stub returned by list_receiving_institutions when PAYMONGO_CASHOUT_MOCK is on.
# PayMongo test mode has no Money Movement product, so the live receiving-institutions
# call is unreachable locally. Shape mirrors PayMongo's JSON:API response so the frontend
# reads attributes.name/code unchanged; names match RECEIVING_INSTITUTION_LOGO_DOMAINS keys
# in src/data/receivingInstitutionLogos.js so logos resolve in the demo.
MOCK_RECEIVING_INSTITUTIONS = {
    'data': [
        {'id': 'mock_ri_gcash', 'type': 'receiving_institution',
         'attributes': {'name': 'GCash', 'code': 'GCASH'}},
        {'id': 'mock_ri_maya', 'type': 'receiving_institution',
         'attributes': {'name': 'Maya', 'code': 'PAYMAYA'}},
        {'id': 'mock_ri_bdo', 'type': 'receiving_institution',
         'attributes': {'name': 'BDO Unibank', 'code': 'BDO'}},
        {'id': 'mock_ri_bpi', 'type': 'receiving_institution',
         'attributes': {'name': 'Bank of the Philippine Islands', 'code': 'BPI'}},
        {'id': 'mock_ri_metrobank', 'type': 'receiving_institution',
         'attributes': {'name': 'Metrobank', 'code': 'METROBANK'}},
        {'id': 'mock_ri_landbank', 'type': 'receiving_institution',
         'attributes': {'name': 'Landbank', 'code': 'LANDBANK'}},
        {'id': 'mock_ri_pnb', 'type': 'receiving_institution',
         'attributes': {'name': 'PNB', 'code': 'PNB'}},
        {'id': 'mock_ri_rcbc', 'type': 'receiving_institution',
         'attributes': {'name': 'RCBC', 'code': 'RCBC'}},
        {'id': 'mock_ri_securitybank', 'type': 'receiving_institution',
         'attributes': {'name': 'Security Bank', 'code': 'SECURITYBANK'}},
        {'id': 'mock_ri_chinabank', 'type': 'receiving_institution',
         'attributes': {'name': 'Chinabank', 'code': 'CHINABANK'}},
        {'id': 'mock_ri_unionbank', 'type': 'receiving_institution',
         'attributes': {'name': 'UnionBank', 'code': 'UNIONBANK'}},
        {'id': 'mock_ri_eastwest', 'type': 'receiving_institution',
         'attributes': {'name': 'EastWest Bank', 'code': 'EASTWEST'}},
    ],
}


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


def to_centavos(amount):
    return int((parse_decimal(amount) * decimal.Decimal('100')).quantize(decimal.Decimal('1')))


def from_centavos(amount):
    return (parse_decimal(amount) / decimal.Decimal('100')).quantize(decimal.Decimal('0.01'))


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
        'fee': from_centavos(attributes.get('fee')),
        'net_amount': from_centavos(attributes.get('net_amount')),
        'raw': response_body,
    }


def list_receiving_institutions():
    if getattr(settings, 'PAYMONGO_CASHOUT_MOCK', False):
        return MOCK_RECEIVING_INSTITUTIONS

    try:
        response = requests.get(
            f'{PAYMONGO_API_BASE_URL}/wallets/receiving_institutions',
            params={'provider': INSTAPAY_PROVIDER},
            headers=get_money_movement_headers(),
            timeout=PAYMONGO_REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise PayMongoCashOutError(
            'Could not reach PayMongo.',
            response_body={'error': str(exc)},
        ) from exc

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
        'amount': to_centavos(amount),
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

    try:
        response = requests.post(
            f'{PAYMONGO_API_BASE_URL}/wallets/{wallet_id}/transactions',
            json={'data': {'attributes': attributes}},
            headers=get_money_movement_headers(),
            timeout=PAYMONGO_REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise PayMongoCashOutError(
            'Could not reach PayMongo.',
            response_body={'error': str(exc)},
        ) from exc

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
