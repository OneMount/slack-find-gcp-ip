import os
import requests
import utils
import secret_utils


def post_message_to_slack(channel, thread, text):
    if not thread:
        return requests.post('https://slack.com/api/chat.postMessage', {
            'token': secret_utils.get_secret('SLACK_FIND_IP_TOKEN'),
            'channel': channel,
            'text': text,
            'unfurl_links': "false",
        }).json()
    else: 
        return requests.post('https://slack.com/api/chat.postMessage', {
            'token': secret_utils.get_secret('SLACK_FIND_IP_TOKEN'),
            'channel': channel,
            'text': text,
            'thread_ts': thread,
            'unfurl_links': "false",
        }).json()