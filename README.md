# ECS-Audit-Log
Audit S3 data access in DELL EMC ECS

Accounting code is based on:
https://github.com/EMCECS/ecs-account-usage

Added audit log feature to audit delete, upload events for S3 protocol.

Usage:
python3.6 account_usage.py -e https://ecsxyz1.abc.com:4443 --token-endpoint https://ecsxyz1.abc.com:4443/login -u <namespace admin ID> -p <namespace admin password> -t <tokenfile.tkn> --no-verify-ssl


