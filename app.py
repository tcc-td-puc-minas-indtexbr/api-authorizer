import json
import os

from chalicelib.boot import register_vendor

# execute before other codes of app
from chalicelib.logging import get_logger

register_vendor()

from chalice import Chalice
from chalice.app import AuthResponse, AuthRoute, CognitoUserPoolAuthorizer
from chalice.app import AuthRequest
from chalicelib import APP_NAME, http_helper, helper

TOKEN_KEY = 'X-API-KEY'
ALLOW = 'Allow'
DENY = 'Deny'

# hashlib.sha224(b"standard_manager_api").hexdigest()
ALLOWED_APPS = {
    "sigo-frontend": "ba85c48ba5c054246a70c3cc8ca4094a87a687490bc695a13c2d321141578a94",
    "standard-manager-api": "40f3d545af024219e77b18fe4fabb06c9d6ef12354cc82caadebf70cc66fd5e9",
    "standard-update-checker": "2b93fc0a90c47d3385c21220ef9a69d976a38c8527fc06bbb1e06d9ae7e37dd4",
    "consulting-manager-api": "0b739891df1281c7fc5a75885049b825ddffc7b3e23b5ff752b6ecb3a7962795",
    "standard-rss-feed-simulator-api": "8f4a82353ec4789f76af116a5419de8f0adb047f5afbf4df4f280f1a4f705a61"
}

AWS_REGION = os.environ['AWS_REGION'] if 'AWS_REGION' in os.environ else None
AWS_ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID'] if 'AWS_ACCOUNT_ID' in os.environ else None
AWS_ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID'] if 'AWS_ACCOUNT_ID' in os.environ else None

app = Chalice(app_name=APP_NAME, debug=helper.debug_mode())


@app.lambda_function()
def auth_token(event, context):
    auth_type = 'TOKEN'
    token = None
    method_arn = ''
    principal_id = 'user'
    api_gateway_arn_tmp = ''
    aws_account_Id = ''
    rest_api_id = ''
    rest_api_resource = ''
    region = ''
    stage = ''
    access_allowed = False

    if 'type' in event:
        auth_type = event['type']

    if 'methodArn' in event:
        method_arn = event['methodArn']
        tmp = event['methodArn'].split(':')
        api_gateway_arn_tmp = tmp[5].split('/')
        aws_account_Id = tmp[4]
        rest_api_id = api_gateway_arn_tmp[0]
        region = api_gateway_arn_tmp[3]
        stage = api_gateway_arn_tmp[1]
        rest_api_resource = tmp[5]

    if 'authorizationToken' in event:
        token = event['authorizationToken']

    # if TOKEN_KEY.lower() in app.current_request.headers:
    #     token = app.current_request.headers[TOKEN_KEY.lower()]

    get_logger().info("Event: {}".format(event))

    auth_request = AuthRequest(auth_type=auth_type, token=token, method_arn=method_arn)
    auth_response = AuthResponse(routes=[], principal_id=principal_id)

    for k, v in ALLOWED_APPS.items():
        if token == v:
            verb = api_gateway_arn_tmp[2] if len(api_gateway_arn_tmp) > 2 else '*'
            resource = api_gateway_arn_tmp[3] if len(api_gateway_arn_tmp) > 3 else '*'

            auth_response = AuthResponse(routes=[
                AuthRoute("/" + resource, [verb])
            ], principal_id=principal_id)
            access_allowed = True

    auth_response_dict = auth_response.to_dict(auth_request)

    if not access_allowed:
        policies = auth_response_dict['policyDocument']
        statements = policies['Statement']
        for k, v in enumerate(statements):
            statements[k]['Effect'] = DENY


    # new! -- add additional key-value pairs associated with the authenticated principal
    # these are made available by APIGW like so: $context.authorizer.<key>
    # additional context is cached
    auth_response_dict['context'] = {
        'key': token  # $context.authorizer.key -> value
    }

    get_logger().info("auth_response_dict: {}".format(auth_response_dict))

    return auth_response_dict

@app.lambda_function()
def auth_request(event, context):
    get_logger().info("Event: {}".format(event))

    auth_type = None
    method_arn = None
    token = None
    auth = None
    aws_account_Id = ''
    rest_api_id = ''
    rest_api_resource = ''
    region = ''
    stage = ''

    api_gateway_arn_tmp = ''
    principal_id = 'user'

    if 'type' in event:
        auth_type = event['type']

    if 'methodArn' in event:
        method_arn = event['methodArn']
        tmp = event['methodArn'].split(':')
        api_gateway_arn_tmp = tmp[5].split('/')
        aws_account_Id = tmp[4]
        rest_api_id = api_gateway_arn_tmp[0]
        region = api_gateway_arn_tmp[3]
        stage = api_gateway_arn_tmp[1]
        rest_api_resource = tmp[5]

    if TOKEN_KEY in event:
        token = event[TOKEN_KEY]

    if 'Authorization' in event:
       auth = event['Authorization']

    auth_request = AuthRequest(auth_type=auth_type, token=token, method_arn=method_arn)
    auth_response = AuthResponse(routes=[], principal_id=principal_id)


    # TOKEN validation
    for k, v in ALLOWED_APPS.items():
        if token == v:
            verb = api_gateway_arn_tmp[2] if len(api_gateway_arn_tmp) > 2 else '*'
            resource = api_gateway_arn_tmp[3] if len(api_gateway_arn_tmp) > 3 else '*'

            auth_response = AuthResponse(routes=[
                AuthRoute("/" + resource, [verb])
            ], principal_id=principal_id)
            access_allowed = True

    auth_response_dict = auth_response.to_dict(auth_request)

    # USer Validation
    authorizer = CognitoUserPoolAuthorizer(
        'indtexbr-pool', provider_arns=['arn:aws:cognito-idp:us-east-1:'+aws_account_Id+':userpool/us-east-1_L7kAaHw2T'])

    if not access_allowed:
        policies = auth_response_dict['policyDocument']
        statements = policies['Statement']
        for k, v in enumerate(statements):
            statements[k]['Effect'] = DENY

    # new! -- add additional key-value pairs associated with the authenticated principal
    # these are made available by APIGW like so: $context.authorizer.<key>
    # additional context is cached
    auth_response_dict['context'] = {
        'key': token  # $context.authorizer.key -> value
    }

    get_logger().info("auth_response_dict: {}".format(auth_response_dict))

    return auth_response_dict


# only for development
# @app.route('/')
# def index():
#     return auth(app.current_request._event_dict, app.current_request.context)

