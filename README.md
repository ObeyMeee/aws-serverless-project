# Aws serverless project

## Run project
To get this project working you need:

```
        1. Create file secret.py in a root directory
        2. Input these constants into file
    
            aws_access_key_id = <your access key>
            aws_secret_access_key = <your secret access key>
            region_name = <your region>
            bucket_name = <your bucket name>
    
        3. in file serverless.yml change in custom/bucket your name of bucket

```
   
Open working directory and type this into terminal window
```
$ serverless deploy
```
You will see which endpoints and functions are available
## Application endpoints

You can do POST request in order to get link to upload object to s3 bucket.

Example of request body is down here:

```json
{
    "file_name": "happy-dog.png",
    "callback_url": "https://webhook.site/4eaddd11-c612-413d-8f10-5d8168dec959"
}
```

```
params:
file_name - name of object which will be saved
callback_url - url which is going to accept POST request passing blob_id using then in GET request 
```

After you do POST request you get response that is similar to this:
```json
{
    "Url to upload": "https://andrrromeda-bucket.s3.amazonaws.com/sad-dog.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=<acces key>%2F20230130%2F<region>%2Fs3%2Faws4_request&X-Amz-Date=20230130T194526Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=901d153158c21d531d7fd67a8a2cd89faa584bd3675cd5e5f9b7cd72c339368c"
}
```

You can upload file to s3 bucket by this link, choosing file and sending PUT request.

After file's successfully uploaded you can do GET request passing blob_id as path parameter to get link to file.
You can get blob_id from DynamoDB table 'blobs' or having glance on response of callback_url
