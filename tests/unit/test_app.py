import json
import unittest

import chalice
from unittest_data_provider import data_provider

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
    return (auth_event1, False), (auth_event2, True)


class AppTestCase(BaseUnitTestCase):

    @data_provider(get_api_auth_event_sample_raw)
    def test_auth(self, event, routes_allowed_is_empty):
        self.logger.info('Running test: %s', get_function_name(__name__))
        lambda_context = FakeLambdaContext()
        auth_response_dict = app.auth(event=event, context=lambda_context)
        # print(auth_response_dict)
        # response_body = auth_response_dict['policyDocument']
        response_body = auth_response_dict

        # self.assertIsInstance(response, chalice.app.Response)
        # response_dict = response.to_dict()

        self.assertTrue("Version" in response_body)
        self.assertTrue("Statement" in response_body)

        is_empty = len(response_body['Statement'][0]['Resource']) > 0
        self.assertEqual(is_empty, routes_allowed_is_empty)


if __name__ == '__main__':
    unittest.main()
