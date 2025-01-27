# set up environment
## EC2
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-tutorial.html
### create the IAM policy
### Create security group to allow inbound traffic
### Launch your instance
### Connect to your instance

## RDS
https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CreateDBInstance.html
https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Troubleshooting.html#CHAP_Troubleshooting.Connecting
### create database and table

```
SHOW DATABASES;
CREATE DATABASE dental_conversation;
use dental_conversation;
SELECT DATABASE();
SHOW TABLES;

CREATE TABLE `user_chat_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `user_name` varchar(255) NOT NULL,
  `chat_count` int DEFAULT '0',
  `patient_details` text,
  `session_id` int DEFAULT NULL,
  `conversation_score` int DEFAULT NULL,
  `publish_conversation` tinyint DEFAULT '0' COMMENT '0 = non-publish, 1 = publish',
  `performance_feedback` text,
  `scenario` varchar(255) DEFAULT NULL,
  `emotion` varchar(255) DEFAULT NULL,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_chat` (`user_id`,`user_name`,`chat_count`),
  UNIQUE KEY `unique_session_id` (`session_id`)
) ENGINE=InnoDB AUTO_INCREMENT=157 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Stores user chat counts, corresponding sessions, and chat quality information'

CREATE TABLE `chat_records` (
  `session_id` int NOT NULL,
  `user_id` int NOT NULL,
  `message_id` int NOT NULL,
  `message` text NOT NULL,
  `quality` enum('good','bad') DEFAULT NULL,
  `user_role` varchar(50) NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`session_id`,`user_id`,`message_id`),
  CONSTRAINT `chat_records_chk_1` CHECK ((`user_role` in (_utf8mb4'dentist',_utf8mb4'patient')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Stores conversation details data'

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `student_number` varchar(255) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) DEFAULT 'normal',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `profile_image` longblob,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Stores user account information, passwords, roles, and avatar'

CREATE TABLE `suggestions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `suggestion_content` text NOT NULL,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Stores suggestion information'

CREATE TABLE `emotion` (
  `emotion_id` int NOT NULL AUTO_INCREMENT,
  `emotion_name` varchar(255) NOT NULL,
  `emotion_type` varchar(255) NOT NULL,
  `description` text,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`emotion_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `scenario` (
  `scenario_id` int NOT NULL AUTO_INCREMENT,
  `scenario_name` varchar(255) NOT NULL,
  `description` text,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`scenario_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

```

# AWS Secrets Manager -> Database Credentials Storage
create new Secrets in :
https://eu-west-2.console.aws.amazon.com/secretsmanager/listsecrets?region=eu-west-2
## Steps
Store a new secret -> Credentials for Amazon RDS database -> input username and password in Credentials -> select database -> next -> Input a secret name -> next ->next -> Store

## Relation with the code
These information will be read by mysql.py

# Setup openai key
create a key in: https://platform.openai.com/settings/organization/api-keys

Store it in AWS Secrets Manager

# Initialize Database
Import data into the emotion table and the scenario table

# Service

http://18.133.23.50:8501

## turn on service
sudo su
python3 -m venv venv
source venv/bin/activate

streamlit run chatstreamlit/login.py
nohup streamlit run chatstreamlit/login.py &

### Check Background Tasks
jobs

### Bring the Task to the Foreground
fg %1
### Stop the Task
press `Ctrl+C` to stop it

# Langchain
## set up environment
{your_env} can be check by `conda env list`
`mkdir -p {your_env}/etc/conda/activate.d`
`cd {your_env}/etc/conda/activate.d`
`vi env_vars.sh`

input the content:
`export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<your-api-key>
export OPENAI_API_KEY=<your-openai-api-key>
`

