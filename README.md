# 🎈 Dental Interaction Simulator

**Dental Interaction Simulator**

The Dental Interaction Simulator is an advanced training platform designed to enhance the skills of dental professionals through realistic simulations. It allows users to engage in lifelike conversations between dentists and patients, focusing on detailed patient information gathering. The platform utilizes cutting-edge AI technology to generate coherent and natural dialogues, helping trainees practice and improve their communication abilities in a controlled, immersive environment.

## Overview of the App

Current pages include:

- Profile
- Communication
- History Conversation

## Where to acess it?
1. Open the link and click the button of Open app: https://dashboard.heroku.com/apps/chatstreamlit
2. Open the link of http://3.8.0.20:8501/

### Get an OpenAI API key

You can get your own OpenAI API key by following the following instructions:

1. Go to https://platform.openai.com/account/api-keys.
2. Click on the `+ Create new secret key` button.
3. Next, enter an identifier name (optional) and click on the `Create secret key` button.

### Enter the OpenAI API key in Streamlit Community Cloud

To set the OpenAI API key as an environment variable in Streamlit apps, do the following:

1. At the lower right corner, click on `< Manage app` then click on the vertical "..." followed by clicking on `Settings`.
2. This brings the **App settings**, next click on the `Secrets` tab and paste the API key into the text box as follows:

```sh
OPENAI_API_KEY='xxxxxxxxxx'
```

## Run it locally

```sh
1. python3 -m venv venv
2. source venv/bin/activate
3. python3 -m pip install -r chatstreamlit/requirements.txt
4. streamlit run chatstreamlit/login.py
```
## Reference
1. Set up to use Amazon EC2: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html
2. How to Deploy a Streamlit Application on Amazon Linux EC2: https://towardsaws.com/how-to-deploy-a-streamlit-application-on-amazon-linux-ec2-9a71593b434
3. streamlit: https://streamlit.io/gallery?category=llms 
4. Information about store secret message in aws: https://www.youtube.com/watch?v=l0tTbavDb7g

