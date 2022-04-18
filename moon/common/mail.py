from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import moon.common.moon_config as moon_config


class MailType(Enum):
    PLAIN = 'plain'
    HTML = 'html'


def send_mail(from_: str, to: str, sub: str, message: str, type_: MailType) -> None:
    mail = MIMEMultipart()
    mail['From'] = from_
    mail['To'] = to
    mail['Subject'] = sub
    mail.attach(MIMEText(message, type_.value))
    session = smtplib.SMTP(moon_config.mail_server_smtp_adr(), moon_config.mail_server_smtp_port())
    session.starttls()
    session.login(moon_config.mail_user(), moon_config.mail_pwd())
    session.sendmail(from_, to, mail.as_string())
    session.quit()
