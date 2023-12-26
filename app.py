from flask import Flask
import requests
from sshtunnel import SSHTunnelForwarder
from flask import request
import botocore.session
import os
from dotenv import load_dotenv

app = Flask(__name__)

key='tmp1.pem'

trustedhost_ip=""

@app.route('/direct')
def direct_hit():
    query = request.args.get('query')
    print("trustedhost_ip:",trustedhost_ip)
    print("query:",query)
    
    # connection ssh with trustedhost
    with SSHTunnelForwarder((trustedhost_ip,22), ssh_username="ubuntu", ssh_pkey=key, remote_bind_address=(trustedhost_ip, 80)) as tunnel:
       url=f"http://{trustedhost_ip}/direct?query={query}"
       print(url)
       result = requests.get(url)
       print(result.text)

    return result.text

@app.route('/custom')
def custom_hit():
    query = request.args.get('query')
    print("trustedhost_ip:",trustedhost_ip)
    print("query:",query)
    
    # connection ssh with trustedhost
    with SSHTunnelForwarder((trustedhost_ip,22), ssh_username="ubuntu", ssh_pkey=key, remote_bind_address=(trustedhost_ip, 80)) as tunnel:
       url=f"http://{trustedhost_ip}/custom?query={query}"
       print(url)
       result = requests.get(url)
       print(result.text)

    return result.text

@app.route('/random')
def random_hit():
    query = request.args.get('query')
    print("proxy_ip:",trustedhost_ip)
    print("query:",query)
    
    # connection ssh with trustedhost
    with SSHTunnelForwarder((trustedhost_ip,22), ssh_username="ubuntu", ssh_pkey=key, remote_bind_address=(trustedhost_ip, 80)) as tunnel:
       url=f"http://{trustedhost_ip}/random?query={query}"
       print(url)
       result = requests.get(url)
       print(result.text)

    return result.text

@app.route('/health')
def health_check():
  # If everything is fine, return a 200 OK response when ping http://your-instance-ip:80/health
  return 'OK', 200

# get trustedhost public ip 
def get_instance_ip():
    session = botocore.session.Session()
    load_dotenv()
    session.set_credentials(
        access_key=os.getenv("ACCESS_KEY_ID"),
        secret_key=os.getenv("SECRET_ACCESS_KEY_ID"),
    )
    ec2_client=session.create_client('ec2',region_name=os.getenv("REGION"))
    
    trustedhost = ec2_client.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:Name', 'Values': ['trustedhost']}
        ]
    )

    trustedhost_found_ip=""

    for reservation in trustedhost['Reservations']:
        for instance in reservation['Instances']:
            print(instance.get('PublicIpAddress'))
            trustedhost_found_ip = instance.get('PublicIpAddress')

    return trustedhost_found_ip

if __name__ == '__main__':
  trustedhost_ip=get_instance_ip()
  app.run(host='0.0.0.0', port=80)