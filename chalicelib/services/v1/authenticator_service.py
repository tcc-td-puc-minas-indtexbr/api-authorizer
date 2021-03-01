import json
import os
import time

import boto3
from chalice import CognitoUserPoolAuthorizer, AuthResponse
from chalice.app import AuthRequest, AuthRoute
from jose import jwk, jwt
from jose.utils import base64url_decode

from chalicelib.helper import open_vendor_file
from chalicelib.logging import get_logger

ALLOWED_APPS = {
    "sigo-frontend": "ba85c48ba5c054246a70c3cc8ca4094a87a687490bc695a13c2d321141578a94",
    "standard-manager-api": "40f3d545af024219e77b18fe4fabb06c9d6ef12354cc82caadebf70cc66fd5e9",
    "standard-update-checker": "2b93fc0a90c47d3385c21220ef9a69d976a38c8527fc06bbb1e06d9ae7e37dd4",
    "consulting-manager-api": "0b739891df1281c7fc5a75885049b825ddffc7b3e23b5ff752b6ecb3a7962795",
    "standard-rss-feed-simulator-api": "8f4a82353ec4789f76af116a5419de8f0adb047f5afbf4df4f280f1a4f705a61"
}


class AuthenticatorService:
    TOKEN_KEY = 'Authorization'
    API_KEY = 'X-API-KEY'
    ALLOW = 'Allow'
    DENY = 'Deny'
    UNIT_TEST_ENV = False

    def __init__(self, logger=None):
        # logger
        self.logger = logger if logger is not None else get_logger()

    def token_auth(self, event):
        auth_type = 'TOKEN'
        api_key = None
        method_arn = ''
        principal_id = 'user'
        api_gateway_arn_tmp = ''

        if 'type' in event:
            auth_type = event['type']

        if 'methodArn' in event:
            method_arn = event['methodArn']
            tmp = event['methodArn'].split(':')
            api_gateway_arn_tmp = tmp[5].split('/')

        if 'authorizationToken' in event:
            api_key = event['authorizationToken']

        get_logger().info("Event: {}".format(event))

        auth_request = AuthRequest(auth_type=auth_type, token=api_key, method_arn=method_arn)

        is_api_key_valid = self.validate_api_key(api_key)

        access_allowed = is_api_key_valid
        if access_allowed:
            verb = api_gateway_arn_tmp[2] if len(api_gateway_arn_tmp) > 2 else '*'
            resource = api_gateway_arn_tmp[3] if len(api_gateway_arn_tmp) > 3 else '*'

            auth_response = AuthResponse(routes=[
                AuthRoute("/" + resource, [verb])
            ], principal_id=principal_id)
        else:
            auth_response = AuthResponse(routes=[
            ], principal_id=principal_id)

        auth_response_dict = auth_response.to_dict(auth_request)

        # deny resources
        if not access_allowed:
            self.deny_resources(auth_response_dict)

        # new! -- add additional key-value pairs associated with the authenticated principal
        # these are made available by APIGW like so: $context.authorizer.<key>
        # additional context is cached
        auth_response_dict['context'] = {
            'key': api_key  # $context.authorizer.key -> value
        }

        return auth_response_dict

    def request_auth(self, event):
        auth_type = None
        method_arn = None
        token = None
        api_key = None
        api_gateway_arn_tmp = ''
        principal_id = 'user'

        if 'type' in event:
            auth_type = event['type']

        if 'methodArn' in event:
            method_arn = event['methodArn']
            tmp = event['methodArn'].split(':')
            api_gateway_arn_tmp = tmp[5].split('/')

        if self.API_KEY in event['headers']:
            api_key = event['headers'][self.API_KEY]

        if self.TOKEN_KEY in event['headers']:
            token = event['headers'][self.TOKEN_KEY]
            token = token.replace('bearer ', '')

        auth_request = AuthRequest(auth_type=auth_type, token=api_key, method_arn=method_arn)

        is_token_valid = self.validate_token(token)
        is_api_key_valid = self.validate_api_key(api_key)

        access_allowed = is_token_valid and is_api_key_valid
        if access_allowed:
            verb = api_gateway_arn_tmp[2] if len(api_gateway_arn_tmp) > 2 else '*'
            resource = api_gateway_arn_tmp[3] if len(api_gateway_arn_tmp) > 3 else '*'

            auth_response = AuthResponse(routes=[
                AuthRoute("/" + resource, [verb])
            ], principal_id=principal_id)
        else:
            auth_response = AuthResponse(routes=[
            ], principal_id=principal_id)

        auth_response_dict = auth_response.to_dict(auth_request)

        # deny resources
        if not access_allowed:
            self.deny_resources(auth_response_dict)

        # new! -- add additional key-value pairs associated with the authenticated principal
        # these are made available by APIGW like so: $context.authorizer.<key>
        # additional context is cached
        auth_response_dict['context'] = {
            'key': api_key  # $context.authorizer.key -> value
        }

        return auth_response_dict

    def validate_token(self, token):
        claims = self.get_claims(token)
        return False if not claims else True

    def deny_resources(self, auth_response_dict):
        policies = auth_response_dict['policyDocument']
        statements = policies['Statement']
        for k, v in enumerate(statements):
            statements[k]['Effect'] = self.DENY

    def get_claims(self, token):
        try:
            app_client_id = os.environ['AWS_POLL_CLIENT_ID'] if 'AWS_POLL_CLIENT_ID' in os.environ else ''
            headers = jwt.get_unverified_header(token)
            kid = headers['kid']
            hmac_keys = json.loads(open_vendor_file('public/jwks.json', 'r').read())
            keys = hmac_keys['keys']
            key = None

            for i in range(len(keys)):
                if kid == keys[i]['kid']:
                    key = keys[i]
                    break

            if not key:
                self.logger.error('Public key not found')
                return False

            # construct the public key
            public_key = jwk.construct(key)
            # get the last two sections of the token,
            # message and signature (encoded in base64)
            message, encoded_signature = str(token).rsplit('.', 1)

            # decode the signature
            decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
            # verify the signature
            if not public_key.verify(message.encode("utf8"), decoded_signature):
                self.logger.error('Signature verification failed')
                return False

            self.logger.info('Signature successfully verified')

            # since we passed the verification, we can now safely
            # use the unverified claims
            claims = jwt.get_unverified_claims(token)
            # additionally we can verify the token expiration
            if time.time() > claims['exp']:
                self.logger.error('Token is expired')
                if not self.UNIT_TEST_ENV:
                    return False
            # and the Audience  (use claims['client_id'] if verifying an access token)
            if 'aud' in claims and claims['aud'] != app_client_id:
                self.logger.error('Token was not issued for this audience')
                return False
            # now we can use the claims
            return claims

        except Exception as err:
            self.logger.error(err)
            return False

    def validate_api_key(self, api_key):
        result = False
        for k, v in ALLOWED_APPS.items():
            if api_key == v:
                result = True
        return result
