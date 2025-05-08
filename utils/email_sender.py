import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def enviar_email(destinatario, asunto, cuerpo):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = destinatario
    msg['Subject'] = asunto

    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_USER, EMAIL_PASS)
            servidor.send_message(msg)
            print(f"✅ Correo enviado a {destinatario}")
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")