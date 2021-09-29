# Find IP tool


## Install & Using

### Install app on slack


Add application to slack channel

Go to channel -> Details -> More -> Add apps -> Search `{app_name}` -> Add to channel

### Using

1. Mention event

* `@{app_name} {ip}`: Reply your message, everyone in the channel can view this message

2. Slashs commands

* `/{command} {ip}`: Reply your message, only visible to you

## Deploy

### Set secret manager: <br/>
  Get value from your slack app: [link](https://api.slack.com/apps) <br/>
  Secret name: `SLACK_FIND_IP_SIGN_SECRET`<br/>
  Secret name: `SLACK_FIND_IP_TOKEN`
```sh
$ export project_id="{example-project}"
$ export SLACK_FIND_IP_SIGN_SECRET="{slack_sign_secret}"
$ export SLACK_FIND_IP_TOKEN="{slack_oauth_token}"
$ export SLACK_FIND_IP_MEMBER_ID="{slack_authen_member}"
$ export SLACK_FIND_IP_GCS_BUCKET="{slack_bucket}"
$ for secret in SLACK_FIND_IP_SIGN_SECRET SLACK_FIND_IP_TOKEN SLACK_FIND_IP_MEMBER_ID SLACK_FIND_IP_GCS_BUCKET; do
$   echo -n ${!secret} | gcloud secrets create ${secret} --project=${project_id} --replication-policy="automatic" --data-file=-
$ done
```
  
### deploy on cloud function:
```sh
$ export project_id="{example-project}"
$ export function_name="{function_name}"
$ export region="{region}"
$ export service_account="{service_account}"
$ cd cloud-function
$ gcloud functions deploy ${function_name} --runtime python37 --trigger-http --region ${region} --env-vars-file=./env.yaml --service-account=${service_account} --project ${project_id}
```

* permission: <br/>
  cloud function service account need permission `roles/storage.objectViewer` on the bucket which store data and `roles/secretmanager.secretAccessor` on project level