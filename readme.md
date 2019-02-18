
# Serverless T.Dev API Poller

## Overview

This example shows how to get started polling data from the [T.Dev Track and Monitor API](https://dev.telstra.com/content/track-and-monitor-api) using the [Serverless Framework](https://serverless.com/) on AWS.  

After the API is polled, JSON responses from T.Dev are validated against a schema and uploaded to a AWS S3 bucket, allowing additional Lambdas to be triggered off the S3 upload event.  

## Prerequisites

On your PC, install:  
- [Serverless](https://serverless.com/) with `npm install serverless -g`  
- [Docker](https://www.docker.com/) for using Serverless plugin [serverless-python-requirements](https://www.npmjs.com/package/serverless-python-requirements)  
- T.Dev API Key and Secret from [dev.telstra.com](https://dev.telstra.com/)  
- [AWS account](https://aws.amazon.com/)  

## Deployment Steps  

1. Store your T.Dev Creds in AWS  
- In the [AWS console](https://aws.amazon.com/console/), browse to AWS Systems Manager > _Parameter Store_ > _Create Parameter_  
- Create a parameter with name _TDevAPIKey_, of Type _String_ and enter your API key for the _Value_ field  
- Create another parameter with name _TDevAPISecret_, of Type _SecureString_ and enter your API Secret for the _Value_ field  
2. Clone this repo to your PC  
3. Configure where your data is stored  
- Browse to the S3 service and create a bucket for your data. If you want to store all data polled, check the S3 bucket option to version your files.  
- Update the environment variable value for DATA_BUCKET in _serverless.yml_ to reflect the bucket name used  
5. Run `sls deploy` to deploy your serverless stack  
6. After waiting for the schedule interval of your Lambda function to pass as defined in _serverless.yml_, check for the data.json in your S3 bucket.

## Todo

- Use the same T.Dev access token until it expires and implement token refresh
