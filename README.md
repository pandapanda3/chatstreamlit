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
Open the link of http://18.133.23.50:8501/ (When the service is up and running)
Or just scan the QR code in the platform.
## How to Setup the Environment?
Refer to the 'Setting Up The Environment' section in the report

## How to Run it？

Log in to the AWS platform, set up the database service on RDS (https://eu-west-2.console.aws.amazon.com/rds/home?region=eu-west-2#databases:), 
and set up the service on EC2 (https://eu-west-2.console.aws.amazon.com/ec2/home?region=eu-west-2#Instances:). 
Then, connect to the server and execute the following operations:
```sh
1. sudo su
2. python3 -m venv venv
3. source venv/bin/activate
4. python3 -m pip install -r chatstreamlit/requirements.txt
(If it raises permission denied issue, use the command : sudo /home/ec2-user/venv/bin/pip install XXX)
(This step is not always necessary.)
5. streamlit run chatstreamlit/login.py or
nohup streamlit run chatstreamlit/login.py &
```
## Results
The Excel files in the "results" folder contain detailed data from running the code for each model.
The "Ethical_Clearance_Letter.pdf" is in the "book" folder.

## The Newest Version of the Code
https://github.com/pandapanda3/chatstreamlit

## Note

When writing dialogues for each character in a document, ensure that the dialogue remains in a single, uninterrupted paragraph without blank lines before continuing.
For example:

**Avoid:**
```
Patient: I brush twice a day, but I rarely floss.
I know I should do it more often, but I just forget or don’t have the time.
Dentist: Flossing is crucial for removing food particles and plaque that your toothbrush can’t reach. Do you use any mouthwash?
```


**Correct format:**
```
Patient: I brush twice a day, but I rarely floss. I know I should do it more often, but I just forget or don’t have the time.
Dentist: Flossing is crucial for removing food particles and plaque that your toothbrush can’t reach. Do you use any mouthwash?
```