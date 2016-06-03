# r53backup
This is a Python script which will read all resource records from Route53 hosted zones from your account, convert it to BIND format and backs it up to both local and S3 storage. 

To use this script:
1) setup boto3 (https://github.com/boto/boto3) 
2) change the variable bucket in line 17 to the desired target S3 bucket
3) change the variable reportPath in line 19 to the desired backup location

