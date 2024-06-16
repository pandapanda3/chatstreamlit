import pymysql
# the data stores in .streamlit/secrets.toml, it's not a good way to expose it to github. It raises security issues.
def get_connection():
    # db_secrets = st.secrets["mysql"]
    return pymysql.connect(
        host='database-dentist.cx6cggcw84g9.eu-west-2.rds.amazonaws.com',
        user='admin',
        password='kcladmin',
        database='dentist_information',
        port=3306,
        charset='utf8mb4'
    )
    # return {
        #     "RDS_HOST": get_ssm_parameter("RDS_HOST"),
        #     "RDS_PORT": int(get_ssm_parameter("RDS_PORT")),
        #     "RDS_DB": get_ssm_parameter("RDS_DB"),
        #     "RDS_USER": get_ssm_parameter("RDS_USER"),
        #     "RDS_PASSWORD": get_ssm_parameter("RDS_PASSWORD"),
        #     "RDS_CHARSET": get_ssm_parameter("RDS_CHARSET")
        # }

# store the secret data in aws
# def get_ssm_parameter(name):
#     ssm = boto3.client('ssm', region_name='London')
#     secret_data_whole = ssm.get_parameter(Name=name, WithDecryption=True)
#     return secret_data_whole['Parameter']['Value']