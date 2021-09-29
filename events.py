import os
import utils
import slack_utils
from google.cloud import storage
import secret_utils


GCS_BUCKET = secret_utils.get_secret(os.environ['GCS_BUCKET'])
GCS_OBJECT = os.environ['GCS_OBJECT']


def url_verification_event(request):
    request_json = request.get_json()
    if request.args and 'challenge' in request.args:
        return request.args.get('challenge')
    elif request_json and 'challenge' in request_json:
        return request_json['challenge']
    else:
        return utils.build_response(200, 'No challenge found. Nothing to do')
        

def app_mention_event(request):
    request_json = request.get_json()
    text = request_json['event']['text']
    params = text.split('>')

    #channel
    channel = request_json['event']['channel']

    #thread
    thread = None
    if 'thread_ts' in request_json['event']:
        thread = request_json['event']['thread_ts']
    elif 'ts' in request_json['event']:
        thread = request_json['event']['ts']

    #write log
    utils.log("{\"event\": \"app mention\",\"user_execute\": \"" + request_json['event']['user'] + "\", \"text_search\": \"" + params[1].lstrip() + "\", \"channel\": \"" + channel + "\", \"thread\": \"" + thread + "\"}")

    if request_json['event']['user'] not in utils.get_slack_id():
        slack_utils.post_message_to_slack(channel, thread, 'Please contact owner to whitelist for using bot')
        return utils.build_response(403, 'Permission denied.')

    if len(params) != 2 or not params[1].strip():
        slack_utils.post_message_to_slack(channel, thread, 'Invalid syntax.')
        return utils.build_response(400, 'Invalid syntax.')

    request_text = str(params[1]).lstrip()    
    
    if validate_ip(request_text) is True:
        gcsfile = get_object()
        message = get_ip_vm(request_text, gcsfile)               
        if message:
            slack_utils.post_message_to_slack(channel, thread, message)
        if not message:
            slack_utils.post_message_to_slack(channel, thread, 'IP not found')
        return utils.build_response(200, 'App mention event successfully')
    slack_utils.post_message_to_slack(channel, thread, 'Invalid input, check your input')   
    return utils.build_response(400, 'Invalid syntax.')        


def app_slash_event(request):
    data = request.form
    params = data['text'].split()
    
    utils.log("{\"event\": \"app splash\", \"user_execute\": \"" + data['user_id'] + "\", \"text_search\": \"" +  data['text'] + "\", \"channel\": \"" + data['channel_id'] + "\", \"user_name\": \"" + data['user_name'] + "\"}")
    if data['user_id'] not in utils.get_slack_id():
        return utils.build_command_response('Due to security policy, please contact cloud team to get yourself whitelist for using find_ip bot')
    if len(params) != 1:
        return 'Invalid command syntax.'
    request_text = str(params[0]).lstrip()       
    if validate_ip(request_text) is True:
        gcsfile = get_object()    
        message = get_ip_vm(request_text, gcsfile)                 
        if len(message):
            return message
        return 'IP not found'
    return utils.build_command_response('Invalid input')        


def get_object():
    client = storage.Client()
    bucket = client.get_bucket(GCS_BUCKET)
    blob = bucket.get_blob(GCS_OBJECT)
    return blob.download_as_string().splitlines()


def get_ip_vm(findip, get_object):   
    for objectline in get_object:
        obj=objectline.split(b',')
        projectid=str(obj[0].decode())
        resourcename=str(obj[1].decode())
        tier=str(obj[2].decode())
        location=str(obj[3].decode())
        address1=str(obj[4].decode())
        address2=str(obj[5].decode())
        tag=str(obj[6].decode())
        vmlink='<https://console.cloud.google.com/compute/instancesDetail/zones/' + location + '/instances/' + resourcename +'?project=' + projectid +'|' + resourcename + '>'
        #format file have public and private IP in column 4 and 5  
        if findip and (findip == address1 or findip == address2):
            #VM_text
            if address1:
                return 'Project: ' + projectid + '\nResource name: ' + vmlink + '\nTier: ' + tier + '\nPublic IP: ' + address1 + '\nInternal IP: ' + address2 + '\nNetwork Tags: [' + tag + ']'
            return 'Project: ' + projectid + '\nResource name: ' + vmlink + '\nTier: ' + tier + '\nAddress: ' + address2 + '\nNetwork Tags: [' + tag + ']'
    return ''


def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True