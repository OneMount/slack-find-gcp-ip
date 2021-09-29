import hmac
import os
import time
import hashlib
import secret_utils

SLACK_SIGN_SECRET_KEY = os.environ['SLACK_SIGN_SECRET_KEY']
SLACK_TIMEOUT_TIME = os.environ['SLACK_TIMEOUT_TIME']
SLACK_MEMBER_ID = os.environ['SLACK_MEMBER_ID']

class ServerException(Exception):
    pass


class AuthenticationException(Exception):
    pass


class BadRequestException(Exception):
    pass


class AccessDeniedException(Exception):
    pass


class ResourceConflictException(Exception):
    pass


class ResourceNotFoundException(Exception):
    pass


def verify_signature(request):
    SLACK_SIGN_SECRET = secret_utils.get_secret(SLACK_SIGN_SECRET_KEY)

    request_timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    # The request timestamp is more than five minutes from local time.
    # It could be a replay attack, so let's ignore it.
    if abs(time.time() - float(request_timestamp)) > int(SLACK_TIMEOUT_TIME):
        raise BadRequestException('The request timestamp is more than five minutes from local time')
    signature = request.headers.get('X-Slack-Signature', '')
    req = str.encode('v0:{}:'.format(request_timestamp)) + request.get_data()
    request_digest = hmac.new(
            str.encode(SLACK_SIGN_SECRET),
            req, hashlib.sha256
        ).hexdigest()
    request_hash = 'v0={}'.format(request_digest)

    if not hmac.compare_digest(request_hash, signature):
        raise AuthenticationException('Invalid request/credentials')

def get_slack_id():
    SLACK_MEMBER=[i.split(":") for i in secret_utils.get_secret(SLACK_MEMBER_ID).split(",")]
    slack_id=[]
    for slack_member_info in SLACK_MEMBER:
        slack_id.append(slack_member_info[1].lstrip())
    return slack_id

def log(message):
    print(message)

def build_command_response(output):
    return output

def build_response(status_code, message):
    log('status_code: %s, message: %s' % (status_code, message))
    return 'status_code: %s, message: %s' % (status_code, message)


def build_error_response(ex):
    if type(ex) is AuthenticationException:
        return build_response(403, {
            'message': ex.message
        })
    if type(ex) is BadRequestException:
        return build_response(400, {
            'message': ex.message
        })
    if type(ex) is ServerException:
        return build_response(500, {
            'message': ex.message
        })
    if type(ex) is AccessDeniedException:
        return build_response(401, {
            'message': ex.message
        })
    if type(ex) is ResourceConflictException:
        return build_response(409, {
            'message': ex.message
        })
    if type(ex) is ResourceNotFoundException:
        return build_response(404, {
            'message': ex.message
        })

    return build_response(500, {
        'message': 'Internal Server Error'
    })


