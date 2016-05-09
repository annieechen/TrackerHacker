import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

fromaddr = "ptrackerhackers@gmail.com"
toaddr = "david.schwartz@yale.edu"

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "overalldata.txt"

body = "Here is today's data"

msg.attach(MIMEText(body, 'plain'))

filename = "overalldata.txt"
attachment = open("/home/pi/overalldata.txt", "rb")

part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "benjaminpi")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
