##  Route53 DNS Backup
##      Exports DNS records in your AWS Route53 account in BIND format
##      writes one copy to local directory and one copy to S3
##      ----------------------
##		Written by: Tan Sze Chern (szechern@gmail.com)
##		Environment: Python 3.x, boto3

import boto3
import sys
import time
import os

class R53Backup(object):

	def __init__(self):

		self.bucket = "<<S3 bucket name>>"

		self.reportPath = "<<Local directory to store the backup>>"

		if not os.path.exists(self.reportPath):
			os.makedirs(self.reportPath)

	def main(self):
		try:
			print("Creating S3 client...")
			s3 = boto3.resource('s3')

			s3folder = time.strftime("%Y%m%d")
			
			print("Creating Route53 client...")
			client = boto3.client("route53")
			
			print("Listing hosted zones...")
			zones = (client.list_hosted_zones()).get('HostedZones')

			for zone in zones:
				zoneId = (zone.get('Id')).replace("/hostedzone/","")
				zoneName = zone.get('Name')

				print("Backing up BIND records for "+zoneName)

				filePostfix = time.strftime("%Y%m%d%I%M%S")
						
				fileName = zoneName
				fileName += filePostfix
				fileName += ".txt"

				bkpFile = self.reportPath
				bkpFile += fileName

				f = open(bkpFile, 'a')
				
				f.write("$ORIGIN "+zoneName)

				recordSets = client.list_resource_record_sets(HostedZoneId=zoneId)
				records = recordSets.get("ResourceRecordSets")

				for record in records:

					recordName = record.get("Name")

					if recordName == zoneName:
						recordName = "@"
					else:
						filterValue = "."+zoneName
						recordName = recordName.replace(filterValue,"")
					if "TTL" in record:
						recordTTL = record.get("TTL")
					else:
						recordTTL = 86400 

					recordType = record.get("Type")

					if "ResourceRecords" in record:
						resRecords = record.get("ResourceRecords")	
						for resRecord in resRecords:
							values = resRecord.get("Value")
							bindRecord = recordName+" "+str(recordTTL)+" IN  "+recordType+" "+resRecord.get("Value")
							
							f.write("\n")
							f.write(bindRecord)
					elif "Failover" in record:
						failoverRecord = record.get("Failover")
						
						setId = record.get("SetIdentifier")
						aliasRecord = record.get("AliasTarget")						

						evalTarget = str(aliasRecord.get("EvaluateTargetHealth")).lower()

						bindRecord = recordName+" "+str(recordTTL)+"  AWS ALIAS  "+recordType+" "+aliasRecord.get("DNSName")+"  "+aliasRecord.get("HostedZoneId")+"  "+evalTarget+" ; "+" AWS routing=\"FAILOVER\" failover=\""+failoverRecord+"\" identifier=\""+setId+"\""
						f.write("\n")
						f.write(bindRecord)					

					elif "AliasTarget" in record:	
						aliasRecord = record.get("AliasTarget")
						
						evalTarget = str(aliasRecord.get("EvaluateTargetHealth")).lower()

						bindRecord = recordName+" "+str(recordTTL)+"  AWS ALIAS  "+recordType+" "+aliasRecord.get("DNSName")+"  "+aliasRecord.get("HostedZoneId")+"  "+evalTarget
						f.write("\n")
						f.write(bindRecord)
					

				print("Backed up to "+bkpFile)

				s3path = s3folder+"/"+fileName

				s3.Object(self.bucket, s3path).put(Body=open(bkpFile,'rb'))
				print("Secondary copy stored in S3 Bucket "+self.bucket+" Object name="+s3path)

		except:
			print(str(sys.exc_info()[0]))


if __name__=='__main__':
	get_instance_details = R53Backup()
	get_instance_details.main()
