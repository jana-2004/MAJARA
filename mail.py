import os
from dotenv import load_dotenv
from mailjet_rest import Client

load_dotenv()
MAILJET_API_SECRET=os.getenv('MAILJET_API_SECRET')
MAILJET_API_KEY=os.getenv('MAILJET_API_KEY')
mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')

def send_email(sender, recipient, content):
    '''content is a dictionary with keys subject, body, htmlpart'''

    data = {
        'Messages': [
            {
                'From': {
                    'Email': sender,
                    'Name': 'MAJARA'
                },
                'To': [
                    {
                        'Email': recipient
                    }
                ],
                **content
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result.status_code, result.json()


def create_mail_verify_message(verification_code):
    return {
        "Subject": "Verify your email address",
        "TextPart": "Please use the following code to verify your email",
        "HTMLPart": f"""
        <h3>Your email verification code: </h3>
        <h2>{verification_code}</h2>
        """
    }

def create_reset_password_message(verification_code):
    return {
        "Subject": "Reset your password",
        "TextPart": "Please use the following code to reset your password",
        "HTMLPart": f"""
        <h3>Your email verification code: </h3>
        <h2>{verification_code}</h2>
        """
    }