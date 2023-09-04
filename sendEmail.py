
# Python3.9 code for sending medication activity as an email

import smtplib
from email.mime.text import MIMEText
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

email_from = 'sender_email@gmail.com'
password = 'qrmd kvkk fkxp jgyn'
email_to = 'receiver_email@gmail.com'

email = MIMEMultipart()
email['From'] = email_from
email['To'] = email_to
email['Subject'] = 'Medication Log'

email.attach(MIMEText("Medication update", 'plain'))
log_file_name = '/home/generic/Emm/medLog.pdf'
log_file = open(log_file_name, 'rb')
payload = MIMEBase('application', 'octate-stream')
payload.set_payload((log_file).read())
encoders.encode_base64(payload)
payload.add_header('Content-Decomposition', 'attachment', filename = log_file_name)
email.attach(payload)
smtp_session = smtplib.SMTP('smtp.gmail.com', 587)
smtp_session.starttls()
smtp_session.login(email_from, password)
log = email.as_string()
smtp_session.sendmail(email_from, email_to, log)
smtp_session.quit()
