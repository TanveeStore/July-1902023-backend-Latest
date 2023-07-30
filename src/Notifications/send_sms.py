# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

def sendsms():
    account_sid = "AC06239581625a8ff13974531f6ef5ad6d"
    auth_token = "0d91418214ad023164d75681d689944b"
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                        body="Send Otp On Your Register Mobile Number.",
                        from_='+19379143458',
                        to='+919422060356'
                    )


    print("Sms Send Successfuly")


    """account_sid = 'AC06239581625a8ff13974531f6ef5ad6d'
    auth_token = "0d91418214ad023164d75681d689944b"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='+19379143458',
        to='+919422060356'
    )

    print("send Otp successfully")"""


    # Find your Account SID at twilio.com/console
    # Provision API Keys at twilio.com/console/runtime/api-keys
    # and set the environment variables. See http://twil.io/secure
    '''account_sid = "AC06239581625a8ff13974531f6ef5ad6d"
    api_key = "0d91418214ad023164d75681d689944b"
    api_secret = os.environ['TWILIO_API_SECRET']
    client = Client(api_key, api_secret, account_sid)

    message = client.messages.create(
        body='This will be the body of the new message!',
        from_='+15017122661',
        to='+15558675310'
    )

    print(message.sid)'''