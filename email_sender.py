import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()

from_email = "secfilingbotgenai@gmail.com"
password = os.getenv("GOOGLE_PASSWORD")

# TODO -> NEED TO MOVE THE CREDENTIALS TO SECRET FILE
def send_email(subject, body, to_emails):
    """
    Simple SMTP based email code.Triggered by the LLM


    :param subject:  The subject of the email
    :param body: The bodu of the email genreally a HTML
    :param to_emails: list of email addresses to send the email to
    :return: succsess if the email is sent
    """
    # Gmail account credentials
    from_email = "secfilingbotgenai@gmail.com"
    password = os.getenv("GOOGLE_PASSWORD")

    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = from_email
    message['Subject'] = subject

    # Attach the HTML body to the email
    message.attach(MIMEText(body, 'html'))

    try:

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        server.login(from_email, password)


        for to_email in to_emails:
            message['To'] = to_email
            server.send_message(message)
            print(f"Email sent to {to_email}")

        return 200

    except Exception as e:
        print(f"Failed to send email: {e}")
        return 400
    finally:
        server.quit()




