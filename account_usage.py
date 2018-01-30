'''
Copyright Dell EMC
This application provide a list of namespace in ECS sorted by their usage of the storage system.

Accounting code is based on:
https://github.com/EMCECS/ecs-account-usage

Updated: 20 Jan 2018
Added audit log feature to audit delete, upload events for S3 protocol.

'''
import operator
import logging
import getpass
import begin
import datetime
import time
import pytz


from ecsclient.common.exceptions import ECSClientException
from ecsclient.client import Client

#Logging parameters
logger = logging.getLogger('account_usage')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('account_usage.log','w')
fh.setLevel(logging.ERROR)
logger.addHandler(fh)

AuditLogFile = r"/var/log/messages"

DELETE="DELETE"
PUT="PUT"

DATETIME=5
MONTH=0
DAY=1
TIME=2
SOURCEIP=8
OBJECTUSER=9
OBJECTNAME=13
BUCKET=12
NAMESPACE=11
OUTPUT=16
SIZE=18

class ECSConsumption(object):
	'''Get user consumption on ECS and print it to the screen'''

	def __init__(self, username, password, token_endpoint, ecs_endpoint,
				 request_timeout, verify_ssl, token_path):
		self.username = username
		self.password = password
		self.token_endpoint = token_endpoint

		self.ecs_endpoint = ecs_endpoint
		self.request_timeout = request_timeout
		self.verify_ssl = verify_ssl
		self.token_path = token_path

	def get_user_consumption(self):
		'''Get the users account usage information'''

		client = Client(username=self.username,
						password=self.password,
						token_endpoint=self.token_endpoint,
						ecs_endpoint=self.ecs_endpoint,
						request_timeout=self.request_timeout,
						verify_ssl=self.verify_ssl,
						token_path=self.token_path, version='3')


		namespaces = client.namespace.list()  # Get all the namespaces in the system
		size_dict = {}
		quota_dict = {}

		for namespace in namespaces['namespace']:
			namespace_id = namespace['id']
			namespace_name = namespace['name']
			logger.debug(namespace_id)

			try:
				namespace_info = client.billing.get_namespace_billing_info(namespace_id)
				size_dict[namespace_name] = int(namespace_info['total_size'])
				quota_info = client.namespace.get_namespace_quota(namespace_id)
				quota_dict[namespace_name] = int(quota_info['blockSize'])
			except ECSClientException:  # Secure buckets dont provide their size
				logger.warning('Error found in namespace: %s\nException: %s\n skipping',
							   namespace['name'], Exception)
				continue

			logger.debug(size_dict)
			logger.debug(quota_dict)
		client.authentication.logout()

		return size_dict, quota_dict


# if __name__ == "__main__":
if begin.start():
	pass

def convert_datetime_timezone(dt, tz1, tz2):
	tz1 = pytz.timezone(tz1)
	tz2 = pytz.timezone(tz2)
	sp = dt.split('T')
	dt = sp[0] + " "+ sp[1]
	dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
	dt = tz1.localize(dt)
	dt = dt.astimezone(tz2)
	dt = dt.strftime("%Y-%m-%d %H:%M:%S")

	return dt
	
def printLog(list, operation):

	
	list[DATETIME]=convert_datetime_timezone(list[DATETIME], "UTC", "Asia/Singapore")
	
	if operation =="UPLOAD":
		print('IP:{0} User:{1} {2} Object:{3} Size:{4} Bucket:{5} Namespace:{6} Date:{7}'.format(list[SOURCEIP],list[OBJECTUSER],operation,list[OBJECTNAME],list[SIZE],list[BUCKET],list[NAMESPACE],list[DATETIME]))
	if operation == "DELETE":
		print('IP:{0} User:{1} {2} Object:{3} Bucket:{4} Namespace:{5} Date:{6}'.format(list[SOURCEIP],list[OBJECTUSER],operation,list[OBJECTNAME],list[BUCKET],list[NAMESPACE],list[DATETIME]))
	print('')

def searchLog(objectuser):

	with open(AuditLogFile) as f:
		f = f.readlines()
	print('========================================================================')
	print('Audit Log:')
	
	for line in f:
		if objectuser in line:
			list=line.split( )
			list[SOURCEIP]=list[SOURCEIP].split(':')[0]
			list[DATETIME]=list[DATETIME].split(',')[0]
			if DELETE in line:
				if list[OUTPUT] == "204":
					printLog(list,DELETE)
			if PUT in line:
				if list[OUTPUT] == "200":
					printLog(list,"UPLOAD")
	print('========================================================================')
					
@begin.start(auto_convert=False)
def run(username='admin',
		password='password',
		token_endpoint='https://portal.ecstestdrive.com/login',
		ecs_endpoint='https://portal.ecstestdrive.com',
		request_timeout=15,
		verify_ssl=False,
		token_path='/tmp'):
	'''
	Creates a simple report using the CLI
	'''

	if password is 'password':
		password = getpass.getpass(prompt='Password: ', stream=None)

	user_dict, quota_dict = ECSConsumption(username, password, token_endpoint, ecs_endpoint, request_timeout,
										   verify_ssl, token_path).get_user_consumption()

	# Display users and utilization
	#print(chr(27) + "[2J")
	print('========================================================================')
	print('{0:50} {1:5} GB'.format('Namespace', 'consumption'))
	print('========================================================================')
	for key, value in sorted(user_dict.items(), key=operator.itemgetter(1)):
		print('{0:50} {1:>5} GB'.format(key, value))
		searchLog(key)

