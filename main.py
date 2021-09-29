import time
import os
import events
import utils


SLACK_RETRY_TIME = os.environ['SLACK_RETRY_TIME']
ROUTES = (
    ('event/url_verification', events.url_verification_event),
    ('event/event_callback/app_mention', events.app_mention_event),
    ('command/findip', events.app_slash_event),
)


def slack_find_ip(request):
    try:
        utils.verify_signature(request)

        # Skip Slack Retry request
        if ('X-Slack-Retry-Num' in request.headers or 'X-Slack-Retry-Reason' in request.headers):
            request_timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
            if abs(time.time() - float(request_timestamp)) < int(SLACK_RETRY_TIME):
                return f'Skip Slack Retry Requests'
        
        request_json = request.get_json()
        route = "unknown"
        
        # Slack Event
        if request.content_type == 'application/json':
            event_type = request_json['type']
            route = 'event/' + event_type

            if 'event' in request_json and 'type' in request_json['event']:
                route += '/' + request_json['event']['type']
        # Slack command
        elif request.content_type == 'application/x-www-form-urlencoded':
            data = request.form
            route = 'command/' + data['command'].strip('/')

        for path, handler in ROUTES:
            if path == route:
                return handler(request)

        utils.log("Couldn't handle route(%s), json(%s)" % (route, request_json))
        raise utils.BadRequestException("Couldn't handle route %s" % (route,))

    except Exception as error:
        utils.log(error)
        return utils.build_error_response(error)
