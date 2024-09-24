import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
from string import Template

host_url = os.getenv("HOSTING_URL")
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_content = template_file.read()
    return Template(template_content)

async def send_email(email: str, name: str, jwt_token: str, mail_type: str = 'onboarding') -> str:
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    link = f"{host_url}/validate?token={jwt_token}"

    sender = {  
      "name": os.getenv("BREVO_SENDER_NAME"),
      "email": os.getenv("BREVO_SENDER_EMAIL")
    }
    
    if mail_type == 'onboarding':
        subject = "Welcome"
        template = read_template('background_tasks/mail_template/onboarding_mail.html')
    elif mail_type == 'magic_link':
        subject = "Magic Link"
        template = read_template('background_tasks/mail_template/magic_mail.html')
    
    # Substitute variables in the template
    html_content = template.substitute(name=name, link=link)
    
    to = [{"email": email, "name": name}]
    params = {"EMAIL": email}
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender, 
        to=to, 
        subject=subject, 
        params=params, 
        html_content=html_content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return api_response.message_id
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)