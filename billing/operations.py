import datetime
import hashlib
import random
import string
import calendar
import os

import base64
import billing.mail_sender as mail_sender
import pdfkit

from Crypto.Cipher import AES
from Crypto import Random
from django.conf import settings


def get_md5_hash(value):
	m = hashlib.md5()
	m.update(value)
	md5 = m.hexdigest()
	return md5


def get_random_string(length=32):
	return ''.join(
		random.choice(
			string.ascii_uppercase + string.digits
		) for _ in range(length)
	)


def decrypt_value(vector, encrypted):
	cifer = AESCipher(vector)
	return cifer.decrypt(encrypted)


def encrypt_value(vector, raw):
	cifer = AESCipher(vector)
	return cifer.encrypt(raw)


def send_doc_to_customer(
	credentials, sender, subject, msg_text,
	to_addresses, cc_addresses, memory_attachment
):
	mail = mail_sender.SMTPEmail()
	mail.SERVER = settings.DEFAULT_MAIL_SERVER
	mail.PORT = settings.DEFAULT_MAIL_SERVER_PORT
	mail.USERNAME = credentials[0]
	mail.PASSWORD = credentials[1]
	mail.SENDER = sender
	mail.TO_ADDRESES = to_addresses
	mail.SUBJECT = subject
	mail.CC_ADDRESES = cc_addresses
	mail.MESSAGE_TEXT = msg_text
	mail.MEMORY_ATTACHMENT = memory_attachment
	return mail.send()


def add_months_to_date(datetime_obj, months_to_add):
	origin_day_in_month = datetime_obj.day

	for x in range(months_to_add):

		month_days = calendar.monthrange(
			datetime_obj.year, datetime_obj.month
		)[1]

		datetime_obj += datetime.timedelta(
			days=month_days - datetime_obj.day + 1
		)

		next_month_days = calendar.monthrange(
			datetime_obj.year, datetime_obj.month
		)[1]

		if x == months_to_add - 1:
			if origin_day_in_month > next_month_days:
				datetime_obj += datetime.timedelta(days=next_month_days - 1)
			else:
				datetime_obj += datetime.timedelta(days=origin_day_in_month - 1)

	return datetime_obj


class PDF(object):
	default_print_options = {
		# 'encoding': "UTF-8",
		'print-media-type': '',
		'disable-smart-shrinking': '',
		'page-size': 'A4',
		'quiet': '',
		'zoom': '0.6',
	}
	memory_file = None
	error = None

	def __init__(self, html, output, print_options=None):
		if settings.WKHTML_BIN_PATH:
			try:
				conf = pdfkit.configuration(
					wkhtmltopdf=os.path.join(settings.BASE_DIR, settings.WKHTML_BIN_PATH)
				)
			except:
				self.error = 'PDF service unavailable!'
		else:
			conf = None

		if not self.error:
			if not print_options:
				print_options = self.default_print_options

			kwargs = {
				'options': print_options,
			}
			if conf:
				kwargs['configuration'] = conf

			if not output:
				self.memory_file = pdfkit.from_string(html, output, **kwargs)
			else:
				pdfkit.from_string(html, output, **kwargs)


class AESCipher(object):

	def __init__(self, key):
		self.bs = 32
		self.key = hashlib.sha256(key.encode()).digest()

	def encrypt(self, raw):
		raw = self._pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

	def _pad(self, s):
		return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

	@staticmethod
	def _unpad(s):
		return s[:-ord(s[len(s) - 1:])]
