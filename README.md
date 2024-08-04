# 🎈 Dental Interaction Simulator

**Dental Interaction Simulator**

The primary goal of this research is to develop a text-to-text communication platform
that facilitates realistic virtual interactions between dental students and virtual patients,
with the model acting as a patient role interacting with the user (dentist). This system
aims to enhance the communication skills of dental students by providing a safe and
controlled environment.
## Overview of the App

Current pages include:

- Profile Page
- Communication Page
- History Conversation Page
- History Detail Conversation Page
- Admin Page

## Where to Acess It?
1. Open the link of http://3.8.0.20:8501/ (When the service is up and running)
2. Open the link and click the button of Open app: https://dashboard.heroku.com/apps/chatstreamlit (The platform is about to be deleted.)

## How to Setup the Environment?
Refer to the 'Setting Up The Environment' section in the report

## How to Run it？

Log in to the AWS platform, set up the database service on RDS (https://eu-west-2.console.aws.amazon.com/rds/home?region=eu-west-2#databases:), 
and set up the service on EC2 (https://eu-west-2.console.aws.amazon.com/ec2/home?region=eu-west-2#Instances:). 
Then, connect to the server and execute the following operations:
```sh
1. python3 -m venv venv
2. source venv/bin/activate
3. python3 -m pip install -r chatstreamlit/requirements.txt
(If it raises permission denied issue, use the command : sudo /home/ec2-user/venv/bin/pip install XXX )
4. streamlit run chatstreamlit/login.py or
nohup streamlit run chatstreamlit/login.py &
```
## Results
The Excel files in the "results" folder contain detailed data from running the code for each model.

## The Newest Version of the Code
https://github.com/pandapanda3/chatstreamlit