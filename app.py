from chalicelib.boot import register_vendor

# execute before other codes of app
from chalicelib.logging import get_logger
from chalicelib.services.v1.authenticator_service import AuthenticatorService

register_vendor()

from chalice import Chalice
from chalicelib import APP_NAME, helper

app = Chalice(app_name=APP_NAME, debug=helper.debug_mode())


@app.lambda_function()
def auth_token(event, context):
    get_logger().info("Event: {}".format(event))

    auth_response_dict = AuthenticatorService().token_auth(event)

    get_logger().info("auth_response_dict: {}".format(auth_response_dict))

    return auth_response_dict

@app.lambda_function()
def auth_request(event, context):
    get_logger().info("Event: {}".format(event))

    auth_response_dict = AuthenticatorService().request_auth(event)

    get_logger().info("auth_response_dict: {}".format(auth_response_dict))

    return auth_response_dict

