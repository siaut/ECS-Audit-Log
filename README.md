# ECS-Audit-Log
Audit S3 data access in DELL EMC ECS 3.1

Accounting code is based on:
https://github.com/EMCECS/ecs-account-usage

Added audit log feature to audit delete, upload events for S3 protocol.

## 1. Configure each ECS node to forward logs to a syslog server(ecs-syslog):

sudo vi /etc/rsyslog.conf

	user.*,local0.*                         -/var/log/ecs-fabric-object.all


	$InputFileName /opt/emc/caspian/fabric/agent/services/object/main/log/datahead-access.log

	$InputFileTag ecs-access:

	$InputFileStateFile ecs-access

	$InputFileSeverity info

	$InputFileFacility local7

	$InputRunFileMonitor

	*.* @@ecs-syslog:514


sudo service rsyslog restart


## 2. Setup a Syslog Server (ecs-syslog) in Centos 7 to receive the audit logs from ECS:

	yum install rsyslog rsyslog-doc

vi /etc/rsyslog.conf


Provides UDP syslog reception

	$ModLoad imudp
	$UDPServerRun 514

 
Provides TCP syslog reception

	$ModLoad imtcp
	$InputTCPServerRun 514

systemctl restart rsyslog.service

## 3. Setup ECS Audit Log:

	yum -y install gcc libffi-devel python-devel openssl-devel
	yum -y install python36u-pip
	pip3.6 install -r requirements.txt

Usage:

	python3.6 account_usage.py -e https://ecsxyz1.abc.com:4443 --token-endpoint https://ecsxyz1.abc.com:4443/login -u <namespace_admin_ID> -p <namespace_admin_password> -t <tokenfile.tkn> --no-verify-ssl

Example Output:
	========================================================================
	Namespace                                          consumption GB
	========================================================================
	demo1                                                 57 GB
	========================================================================
	Audit Log:
	IP:x.x.x.x User:user1 UPLOAD Object:greenhouse.pptx Size:8388608 Bucket:bucket1 Namespace:demo1 Date:2018-04-23 10:30:21

	IP:x.x.x.x User:user1 UPLOAD Object:snapshot.jpg Size:108622 Bucket:bucket1 Namespace:demo1 Date:2018-04-23 11:26:03

	IP:x.x.x.x User:user1 DELETE Object:greenhouse.pptx Bucket:bucket1 Namespace:demo1 Date:2018-04-23 11:27:07

	IP:x.x.x.x User:user1 UPLOAD Object:img_1682.jpg Size:3552439 Bucket:bucket1 Namespace:demo1 Date:2018-04-23 11:26:39

	========================================================================

