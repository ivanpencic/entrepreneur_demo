import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import COMMASPACE, formatdate
from email import encoders


class SMTPEmail:
	SERVER = ''
	PORT = 0
	USERNAME = ''
	PASSWORD = ''
	SENDER = ''
	TO_ADDRESES = []
	SUBJECT = ''
	ATTACH_IMAGE_LOCATIONS = []
	HTML_MESSAGE = None
	CC_ADDRESES = []
	MESSAGE_TEXT = ''
	ATTACH_LOCATIONS = []
	MEMORY_ATTACHMENT = []

	def send(self):
		try:
			msg = MIMEMultipart('mixed')
			msg['From'] = self.SENDER
			msg['To'] = ', '.join(self.TO_ADDRESES)
			msg['Cc'] = ', '.join(self.CC_ADDRESES)
			msg['Date'] = formatdate(localtime=True)
			msg['Subject'] = self.SUBJECT
			msg.preamble = 'This is a multi-part message in MIME format.'
			msgAlternative = MIMEMultipart('alternative')
			msgAlternative.attach(MIMEText(self.MESSAGE_TEXT, 'plain', "UTF-8"))

			if self.HTML_MESSAGE:
				msgAlternative.attach(MIMEText(self.HTML_MESSAGE, 'html', "UTF-8"))

			msgRelated = MIMEMultipart('related')
			msgRelated.attach(msgAlternative)

			for image_attachment in self.ATTACH_IMAGE_LOCATIONS:
				attach_img = open(image_attachment, 'rb')
				image = MIMEImage(attach_img.read())
				attach_img.close()
				image.add_header('Content-ID', '<%s>' % os.path.basename(image_attachment))
				image.add_header(
					'Content-Disposition',
					'inline; filename="%s"' % os.path.basename(image_attachment)
				)
				msgRelated.attach(image)

			msg.attach(msgRelated)

			for f in self.ATTACH_LOCATIONS:
				part = MIMEBase('application', "octet-stream")
				part.set_payload(open(f, "rb").read())
				encoders.encode_base64(part)
				part.add_header(
					'Content-Disposition',
					'attachment; filename="%s"' % os.path.basename(f)
				)
				msg.attach(part)

			for f, f_name in self.MEMORY_ATTACHMENT:
				part = MIMEBase('application', "octet-stream")
				part.set_payload(f)
				encoders.encode_base64(part)
				part.add_header(
					'Content-Disposition',
					'attachment; filename="%s"' % f_name
				)
				msg.attach(part)

			smtp = smtplib.SMTP_SSL(self.SERVER, self.PORT)
			smtp.login(self.USERNAME, self.PASSWORD)
			smtp.sendmail(
				self.SENDER, self.TO_ADDRESES + self.CC_ADDRESES, msg.as_string()
			)
			smtp.quit()
			return True, 'success'

		except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused) as err:
			return False, err
