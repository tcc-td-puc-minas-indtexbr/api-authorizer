import json
import unittest

import chalice
from unittest_data_provider import data_provider

from chalicelib.services.v1.authenticator_service import AuthenticatorService
from tests.unit.mocks.aws_lambda_mock import FakeLambdaContext
from tests.unit.testutils import BaseUnitTestCase, get_function_name
import app
from app import ALLOWED_APPS


def get_api_auth_event_sample_raw():
    auth_event1 = {
        "type": "TOKEN",
        "authorizationToken": "incoming-client-token",
        "methodArn": "arn:aws:execute-api:sa-east-1:123456789012:zp8i9o3hna/api/GET/{proxy+}"
    }
    auth_event2 = {
        "type": "TOKEN",
        "authorizationToken": ALLOWED_APPS["sigo-frontend"],
        "methodArn": "arn:aws:execute-api:sa-east-1:123456789012:zp8i9o3hna/api/GET/{proxy+}"
    }
    auth_event3 = {
        "type": "TOKEN",
        "authorizationToken": ALLOWED_APPS["sigo-frontend"],
        "methodArn": "arn:aws:execute-api:sa-east-1:123456789012:zp8i9o3hna/api/GET/feed"
    }

    # return (auth_event1, False), (auth_event2, True), (auth_event3, True)
    return (auth_event3, True),


def get_api_auth_request_sample_raw():
    auth_event1 = {'type': 'REQUEST', 'methodArn': 'arn:aws:execute-api:sa-east-1:821579492372:zp8i9o3hna/api/GET/ping',
                   'resource': '/ping', 'path': '/sigo-standard-rss/ping', 'httpMethod': 'GET',
                   'headers': {
                       'Accept': '*/*',
                       'Accept-Encoding': 'gzip, deflate, br',
                       'Authorization': 'bearer eyJraWQiOiJyYmpJZFJha281eDJDQkpqXC83XC9JOEVZSkhLRCtxQlFaSEFFaDBLR1wvbDk4PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI3MzhhZGU2Yi1iNWRhLTQzNDMtYTM0ZC05MTBmZWQzYjhmNjUiLCJjb2duaXRvOmdyb3VwcyI6WyJhZG1pbiJdLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfTDdrQWFIdzJUIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjb2duaXRvOnVzZXJuYW1lIjoiYW5kZXJzb24uY29udHJlaXJhQGdtYWlsLmNvbSIsImF1ZCI6IjM3a2k4bDY1MnU2NGNwcTZlbGlyMnJyNXY5IiwiZXZlbnRfaWQiOiIzMTgyYTlkOC02YWQ5LTQ2ODYtYWMzOC1jMzI1ZjZlNDcyZWQiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTYxNDU2MjU0MiwibmFtZSI6IlVzZXJuYW1lIiwicGhvbmVfbnVtYmVyIjoiKzU1NDE5ODg3OTI1NzAiLCJleHAiOjE2MTQ1NzMzNDIsImlhdCI6MTYxNDU2MjU0MiwiZW1haWwiOiJhbmRlcnNvbi5jb250cmVpcmFAZ21haWwuY29tIn0.l12a7wHG6RKJ-SHLTK1j7OyGmyJWmeEat67eGDyxbF-owgDi4t8ZMZauO7HplU8Px2yeMFncVY7Hc2I3v6eEg-oFGVEgVgYTfx583ia7n3MXkMWOpq79GVY3U_fQGHdO4CqcYnYwZuhS676pGE0PlqqAlui_PS9EMlZYZX73gfywnKcHg9yhtXdQoDjdxHturZojSPuZa72iOyRPR0fsE5cpCnHkDhIebjpE6qqAfj9D-teWrCX95x5H6duN3vV4Z3_GNbAHAQ4KLR4rHF9KALVGdax1a6SNU9ElGOcvi8p3siU33jl2qbiJMPU47WdhzzTVp9QejShMVAkYhU1udQ',
                       'Cache-Control': 'no-cache', 'CloudFront-Forwarded-Proto': 'https',
                       'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false',
                       'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false',
                       'CloudFront-Viewer-Country': 'BR', 'Host': 'services.hagatus.com.br',
                       'Postman-Token': '9b7e3a0d-f832-4743-b860-8ed5b1d214e6',
                       'User-Agent': 'PostmanRuntime/7.26.8',
                       'Via': '1.1 9cf503db57c8ad049bb21868d2e4bc2c.cloudfront.net (CloudFront)',
                       'X-Amz-Cf-Id': 'WWFNUK59QjCBjFZNqtSbSEHqARR5TRrmvFasunonDZS6dTuWxRzoyg==',
                       'X-Amzn-Trace-Id': 'Root=1-603c1562-08aa04b94ad1b3cc3ec34869',
                       'X-API-KEY': 'ba85c48ba5c054246a70c3cc8ca4094a87a687490bc695a13c2d321141578a94',
                       'X-Forwarded-For': '177.132.7.105, 52.46.43.154', 'X-Forwarded-Port': '443',
                       'X-Forwarded-Proto': 'https'},
                   'multiValueHeaders': {
                       'Accept': ['*/*'],
                       'Accept-Encoding': ['gzip, deflate, br'],
                       'Authorization': [
                       'bearer eyJraWQiOiJyYmpJZFJha281eDJDQkpqXC83XC9JOEVZSkhLRCtxQlFaSEFFaDBLR1wvbDk4PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI3MzhhZGU2Yi1iNWRhLTQzNDMtYTM0ZC05MTBmZWQzYjhmNjUiLCJjb2duaXRvOmdyb3VwcyI6WyJhZG1pbiJdLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfTDdrQWFIdzJUIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjb2duaXRvOnVzZXJuYW1lIjoiYW5kZXJzb24uY29udHJlaXJhQGdtYWlsLmNvbSIsImF1ZCI6IjM3a2k4bDY1MnU2NGNwcTZlbGlyMnJyNXY5IiwiZXZlbnRfaWQiOiIzMTgyYTlkOC02YWQ5LTQ2ODYtYWMzOC1jMzI1ZjZlNDcyZWQiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTYxNDU2MjU0MiwibmFtZSI6IlVzZXJuYW1lIiwicGhvbmVfbnVtYmVyIjoiKzU1NDE5ODg3OTI1NzAiLCJleHAiOjE2MTQ1NzMzNDIsImlhdCI6MTYxNDU2MjU0MiwiZW1haWwiOiJhbmRlcnNvbi5jb250cmVpcmFAZ21haWwuY29tIn0.l12a7wHG6RKJ-SHLTK1j7OyGmyJWmeEat67eGDyxbF-owgDi4t8ZMZauO7HplU8Px2yeMFncVY7Hc2I3v6eEg-oFGVEgVgYTfx583ia7n3MXkMWOpq79GVY3U_fQGHdO4CqcYnYwZuhS676pGE0PlqqAlui_PS9EMlZYZX73gfywnKcHg9yhtXdQoDjdxHturZojSPuZa72iOyRPR0fsE5cpCnHkDhIebjpE6qqAfj9D-teWrCX95x5H6duN3vV4Z3_GNbAHAQ4KLR4rHF9KALVGdax1a6SNU9ElGOcvi8p3siU33jl2qbiJMPU47WdhzzTVp9QejShMVAkYhU1udQ'],
                                         'Cache-Control': ['no-cache'], 'CloudFront-Forwarded-Proto': ['https'],
                                         'CloudFront-Is-Desktop-Viewer': ['true'],
                                         'CloudFront-Is-Mobile-Viewer': ['false'],
                                         'CloudFront-Is-SmartTV-Viewer': ['false'],
                                         'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-Country': ['BR'],
                                         'Host': ['services.hagatus.com.br'],
                                         'Postman-Token': ['9b7e3a0d-f832-4743-b860-8ed5b1d214e6'],
                                         'User-Agent': ['PostmanRuntime/7.26.8'],
                                         'Via': ['1.1 9cf503db57c8ad049bb21868d2e4bc2c.cloudfront.net (CloudFront)'],
                                         'X-Amz-Cf-Id': ['WWFNUK59QjCBjFZNqtSbSEHqARR5TRrmvFasunonDZS6dTuWxRzoyg=='],
                                         'X-Amzn-Trace-Id': ['Root=1-603c1562-08aa04b94ad1b3cc3ec34869'], 'X-API-KEY': [
                           'ba85c48ba5c054246a70c3cc8ca4094a87a687490bc695a13c2d321141578a94'],
                                         'X-Forwarded-For': ['177.132.7.105, 52.46.43.154'],
                                         'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']},
                   'queryStringParameters': {}, 'multiValueQueryStringParameters': {}, 'pathParameters': {},
                   'stageVariables': {},
                   'requestContext': {'resourceId': '4hmocy', 'resourcePath': '/ping', 'httpMethod': 'GET',
                                      'extendedRequestId': 'behHdHH4mjQFbug=',
                                      'customDomain': {'basePathMatched': 'sigo-standard-rss'},
                                      'requestTime': '28/Feb/2021:22:12:50 +0000', 'path': '/sigo-standard-rss/ping',
                                      'accountId': '821579492372', 'protocol': 'HTTP/1.1', 'stage': 'api',
                                      'domainPrefix': 'services', 'requestTimeEpoch': 1614550370871,
                                      'requestId': '57614d25-6aac-4134-9bb0-2283e1e7f06e',
                                      'identity': {'cognitoIdentityPoolId': None, 'cognitoIdentityId': None,
                                                   'apiKey': 'ba85c48ba5c054246a70c3cc8ca4094a87a687490bc695a13c2d321141578a94',
                                                   'principalOrgId': None, 'cognitoAuthenticationType': None,
                                                   'userArn': None, 'userAgent': 'PostmanRuntime/7.26.8',
                                                   'accountId': None, 'caller': None, 'sourceIp': '177.132.7.105',
                                                   'accessKey': None, 'cognitoAuthenticationProvider': None,
                                                   'user': None}, 'domainName': 'services.hagatus.com.br',
                                      'apiId': 'zp8i9o3hna'}}

    # return (auth_event1, False), (auth_event2, True), (auth_event3, True)
    return (auth_event1, True),


class AppTestCase(BaseUnitTestCase):

    @data_provider(get_api_auth_event_sample_raw)
    def test_auth_token(self, event, routes_allowed_is_empty):
        self.logger.info('Running test: %s', get_function_name(__name__))
        lambda_context = FakeLambdaContext()
        auth_response_dict = app.auth_token(event=event, context=lambda_context)
        # print(auth_response_dict)
        response_body = auth_response_dict['policyDocument']
        # response_body = auth_response_dict

        # self.assertIsInstance(response, chalice.app.Response)
        # response_dict = response.to_dict()

        self.assertTrue("Version" in response_body)
        self.assertTrue("Statement" in response_body)

        is_empty = len(response_body['Statement'][0]['Resource']) > 0
        self.assertEqual(is_empty, routes_allowed_is_empty)

    @data_provider(get_api_auth_request_sample_raw)
    def test_auth_request(self, event, routes_allowed_is_empty):
        self.logger.info('Running test: %s', get_function_name(__name__))
        lambda_context = FakeLambdaContext()

        # ignora tokens expirados
        AuthenticatorService.UNIT_TEST_ENV = True

        auth_response_dict = app.auth_request(event=event, context=lambda_context)
        # print(auth_response_dict)
        response_body = auth_response_dict['policyDocument']
        # response_body = auth_response_dict

        # self.assertIsInstance(response, chalice.app.Response)
        # response_dict = response.to_dict()

        self.assertTrue("Version" in response_body)
        self.assertTrue("Statement" in response_body)

        is_empty = len(response_body['Statement'][0]['Resource']) > 0
        self.assertEqual(is_empty, routes_allowed_is_empty)


if __name__ == '__main__':
    unittest.main()
