# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import calendar
from django.db import connection
from django.db import transaction
from django.db import models
from django.contrib.auth.models import User as auth_user
from decimal import Decimal
from django.urls import reverse
import billing.operations as operations
import billing.permissions as permissions
import billing.gui as gui
from django.db.models import Sum
import company.settings as settings


class Language(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name


class Translation(models.Model):
	id = models.AutoField(primary_key=True)
	target_text = models.CharField(max_length=500)
	translation = models.CharField(max_length=500)
	language = models.ForeignKey(Language, on_delete=models.CASCADE)

	def __str__(self):
		if self.target_text != self.translation:
			status = '<OK>'
		else:
			status = '<MISSING>'

		return f"{status} {self.target_text} {self.language.name}"

	@classmethod
	def translate(cls, request, target_text, language_id):
		if settings.APP_LANGAUGE_ID == language_id:
			return target_text

		try:
			return cls.objects.filter(
				**{'target_text': target_text, 'language__id': language_id}
			)[0].translation
		except:
			t = Translation()
			t.target_text = target_text
			t.translation = target_text
			t.language = Language.objects.get(id=language_id)
			t.save()

			return target_text


class Template(models.Model):
	id = models.AutoField(primary_key=True)
	location = models.CharField(max_length=500)

	def __str__(self):
		return self.location


class PersonalData(models.Model):
	id = models.AutoField(primary_key=True)
	first_name_enc = models.CharField(max_length=80)
	last_name_enc = models.CharField(max_length=80)
	address_enc = models.CharField(max_length=300, blank=True)
	salt = models.CharField(max_length=300, null=True)

	def __str__(self):
		return "%s %s %s" % (
			str(self.id),
			operations.decrypt_value(
				self.salt,
				self.first_name_enc,
			),
			operations.decrypt_value(self.salt, self.last_name_enc))

	def full_name(self):
		self = self.decrypt()
		return self.first_name_enc + ' ' + self.last_name_enc

	def decrypt(self):
		self.first_name_enc = operations.decrypt_value(
			self.salt, self.first_name_enc
		)
		self.last_name_enc = operations.decrypt_value(
			self.salt, self.last_name_enc
		)
		self.address_enc = operations.decrypt_value(
			self.salt, self.address_enc
		)
		return self

	def clean(self):
		if not self.id:
			self.salt = operations.get_random_string()

		self.first_name_enc = operations.encrypt_value(
			self.salt, self.first_name_enc
		).decode("utf-8")
		self.last_name_enc = operations.encrypt_value(
			self.salt, self.last_name_enc
		).decode("utf-8")
		self.address_enc = operations.encrypt_value(
			self.salt, self.address_enc
		).decode("utf-8")


class Email(models.Model):
	id = models.AutoField(primary_key=True)
	personal_data = models.ForeignKey(PersonalData, on_delete=models.CASCADE)
	email_enc = models.CharField(max_length=200)
	email_password_enc = models.CharField(max_length=200, blank=True, default='')
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return operations.decrypt_value(self.personal_data.salt, self.email_enc)

	def decrypt(self):
		self.email_enc = operations.decrypt_value(
			self.personal_data.salt, self.email_enc
		)
		self.email_password_enc = operations.decrypt_value(
			self.personal_data.salt,
			self.email_password_enc
		)
		return self

	def clean(self):
		self.email_enc = operations.encrypt_value(
			self.personal_data.salt, self.email_enc
		).decode("utf-8")
		self.email_password_enc = operations.encrypt_value(
			self.personal_data.salt, self.email_password_enc
		).decode("utf-8")


class Phone(models.Model):
	id = models.AutoField(primary_key=True)
	personal_data = models.ForeignKey(PersonalData, on_delete=models.CASCADE)
	phone_enc = models.CharField(max_length=200)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.phone_enc


class Country(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=30)

	def __str__(self):
		return self.name


class City(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=30)
	country = models.ForeignKey(Country, on_delete=models.CASCADE)

	def __str__(self):
		return self.name


class Bank(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	address = models.CharField(max_length=200)
	zip_code = models.CharField(max_length=30)
	city = models.ForeignKey(City, on_delete=models.CASCADE)
	country = models.ForeignKey(Country, on_delete=models.CASCADE)

	def __str__(self):
		return self.name


class Company(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=300)
	reg_no = models.CharField(max_length=30)
	pib = models.CharField(max_length=30, blank=True)
	apr = models.CharField(max_length=30, blank=True)
	address = models.CharField(max_length=300)
	activity_code = models.CharField(max_length=30)
	city = models.ForeignKey(City, on_delete=models.CASCADE)
	country = models.ForeignKey(Country, on_delete=models.CASCADE)
	name_pt1 = models.CharField(max_length=150, blank=True)
	name_pt2 = models.CharField(max_length=150, blank=True)
	bank_account_id = models.CharField(max_length=100, blank=True)

	def __str__(self):
		return self.name


class Currency(models.Model):
	id = models.AutoField(primary_key=True)
	identifier = models.CharField(max_length=10)

	def __str__(self):
		return self.identifier


class CurrencyRelation(models.Model):
	id = models.AutoField(primary_key=True)
	from_currency = models.ForeignKey(
		Currency, related_name='from_currency', on_delete=models.CASCADE
	)
	to_currency = models.ForeignKey(
		Currency, related_name='to_currency', on_delete=models.CASCADE
	)
	value = models.DecimalField(decimal_places=15, max_digits=30)
	relation_date = models.DateField()

	def __str__(self):
		return "%s %s %s" % (
			self.relation_date,
			self.from_currency.identifier,
			self.to_currency.identifier
		)


class Issuer(models.Model):
	id = models.AutoField(primary_key=True)
	date_added = models.DateTimeField(auto_now_add=True)
	personal_data = models.ForeignKey(
		PersonalData, null=True, on_delete=models.CASCADE
	)
	user = models.ForeignKey(
		auth_user, null=True, blank=True, on_delete=models.CASCADE
	)
	company = models.ForeignKey(Company, on_delete=models.CASCADE)
	finance_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

	def __str__(self):
		return self.company.name


class Customer(models.Model):
	id = models.AutoField(primary_key=True)
	date_added = models.DateTimeField(auto_now_add=True)
	personal_data = models.ForeignKey(
		PersonalData, null=True, on_delete=models.CASCADE
	)
	user = models.ForeignKey(
		auth_user, null=True, on_delete=models.CASCADE, blank=True
	)
	issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE)
	company = models.ForeignKey(
		Company, on_delete=models.CASCADE, null=True, blank=True
	)
	invoice_language = models.ForeignKey(Language, on_delete=models.CASCADE)
	invoice_template = models.ForeignKey(Template, on_delete=models.CASCADE)
	agreement_date = models.DateField()

	def __str__(self):
		return self.personal_data.__str__()

	@classmethod
	def format_customer_company_for_greed(cls, request, querry_filter):
		gv_name = 'Customers'
		rows = cls.objects.filter(**querry_filter)
		actions = permissions.filter_grid_actions(request, [
			[
				gui.grid_action(
					request,
					"<i class='fas fa-plus' style='font-size:24px'></i>",
					[
						gv_name,
						'/customers/<int:customer_id>/offers/',
						'<int:customer_id>',
						'0',
						'Please select grid value!',
						'Assets'
					]
				), permissions.allow_any
			],
			[
				gui.grid_action(
					request,
					"<i class='fas fa-list' style='font-size:24px'></i>",
					[
						gv_name,
						'/customers/<int:customer_id>/assets/', '<int:customer_id>',
						'0',
						'Please select grid value!',
						'Assets'
					]
				), permissions.allow_any],

		]), ['Assets']
		headers = ['ID', 'Company', "Name"]
		formated = []
		for x in rows:
			x.personal_data.decrypt()
			formated.append([x.id, x.company.name, x.personal_data.first_name_enc])
		return gv_name, formated, headers, actions


class CompanyBank(models.Model):
	id = models.AutoField(primary_key=True)
	company = models.ForeignKey(Company, on_delete=models.CASCADE)
	bank = models.ForeignKey(Bank, on_delete=models.CASCADE)

	def __str__(self):
		return self.company.__str__()


class Discount(models.Model):
	id = models.AutoField(primary_key=True)
	percent = models.DecimalField(decimal_places=15, max_digits=30)
	fixed_discount = models.DecimalField(
		default=0,
		decimal_places=15,
		max_digits=30
	)
	fixed_price = models.DecimalField(
		null=True,
		default=0,
		decimal_places=15,
		max_digits=30
	)

	class Meta:
		unique_together = ('percent', 'fixed_discount', 'fixed_price')

	def __str__(self):
		return 'p:%.2f%% fixd:%.2f fixp:%.2f ' % (
			self.percent,
			self.fixed_discount,
			self.fixed_price
		)


class Duration(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)
	no_seconds = models.IntegerField()
	no_days = models.IntegerField()
	no_months = models.IntegerField()

	def __str__(self):
		return self.name


class CompanyBankAccount(models.Model):
	id = models.AutoField(primary_key=True)
	account_number = models.CharField(max_length=100)
	aba = models.CharField(max_length=100, null=True, blank=True)
	chips_uid = models.CharField(max_length=100, null=True, blank=True)
	swift = models.CharField(max_length=100, null=True, blank=True)
	iban = models.CharField(max_length=100, null=True, blank=True)
	currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
	company_bank = models.ForeignKey(CompanyBank, on_delete=models.CASCADE)

	def __str__(self):
		return "%s %s" % (str(self.company_bank), str(self.currency), )


class PaymenCode(models.Model):
	id = models.AutoField(primary_key=True)
	code = models.CharField(max_length=50)
	description = models.CharField(max_length=200)

	def __str__(self):
		return self.description


class Asset(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200)
	date_added = models.DateTimeField(auto_now_add=True)
	allow_multiple = models.BooleanField()

	def __str__(self):
		return self.description


class AssetPrice(models.Model):
	id = models.AutoField(primary_key=True)
	asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
	price = models.DecimalField(decimal_places=15, max_digits=30)
	currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
	duration = models.ForeignKey(Duration, on_delete=models.CASCADE)
	valid_from = models.DateField()
	valid_to = models.DateField(null=True, blank=True)

	def __str__(self):
		return "%s %s (%s %s)" % (
			self.asset,
			self.duration.name,
			self.price,
			self.currency.identifier
		)


class Bundle(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200)
	valid_from = models.DateField()
	valid_to = models.DateField(null=True, blank=True)

	def __str__(self):
		return self.name


class PaymentType(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name


class BundleAssetPrice(models.Model):
	id = models.AutoField(primary_key=True)
	issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE)
	bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
	asset_price = models.ForeignKey(AssetPrice, on_delete=models.CASCADE)
	payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
	discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

	def __str__(self):
		return "%s %s" % (self.asset_price, self.bundle.name)

	@classmethod
	def get_available_bundles(cls, request):
		bundles = cls.objects.all().values_list(
			"id",
			"bundle__name",
			'asset_price__asset__name'
		)
		return [[x, y + ' ' + z] for x, y, z in bundles]


class InvoiceType(models.Model):
	id = models.AutoField(primary_key=True)
	identifier = models.CharField(max_length=50)

	def __str__(self):
		return self.identifier


class Invoice(models.Model):
	id = models.AutoField(primary_key=True)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	invoice_number = models.CharField(max_length=50)
	number = models.IntegerField()
	year = models.IntegerField()
	invoice_type = models.ForeignKey(InvoiceType, on_delete=models.CASCADE)
	due_date = models.DateField(null=True)
	invoice_date = models.DateField()
	is_sent = models.BooleanField(default=False)
	date_added = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('number', 'invoice_type', 'year')

	@classmethod
	def get_payment(cls, id):
		invoice_item = InvoiceItem.objects.filter(
			**{'invoice__id': id}
		)[0]
		order_payment = OrderPayment.objects.filter(
			**{'order__id': invoice_item.order.id}
		)[0]
		return order_payment.payment

	@classmethod
	def get_total(cls, id):
		invoice_items = InvoiceItem.objects.filter(**{'invoice__id': id})
		invoice = cls.objects.get(id=id)
		finance_currency = invoice.customer.issuer.finance_currency.identifier
		invoice_total = 0
		currency = ''
		for item in invoice_items:
			currency = item.order.bundle_asset_price.\
				asset_price.currency.identifier
			invoice_total += item.order.total

		try:
			if currency == finance_currency:
				currency_value = 1
			else:
				currency_value = CurrencyRelation.objects.filter(**{
					'relation_date': invoice.invoice_date,
					'from_currency__identifier': currency,
					'to_currency__identifier': finance_currency
				})[0].value
		except:
			currency_value = 0

		return invoice_total, currency, currency_value

	@classmethod
	def get_kpo_for_year(cls, year):
		issuer = Issuer.objects.all()[0]
		issuer_finance_currency = issuer.finance_currency.identifier

		data_rows = []
		inv_data = cls.objects.filter(invoice_date__year=year)
		for inv in inv_data:
			invoice_total, currency, finance_currency_relation = cls.get_total(inv.id)
			invoice_total_in_origin_currency = '%s %s' % (
				round(invoice_total, 2), currency,
			)
			invoice_total_in_finance_currency = '%s %s' % (
				round(invoice_total * finance_currency_relation, 2),
				issuer_finance_currency,
			)
			data_rows.append([
				inv.number,
				'Faktura %s, %s, (%s x %s)' % (
					inv.invoice_number,
					inv.invoice_date.strftime("%d.%m.%Y"),
					invoice_total_in_origin_currency,
					round(finance_currency_relation, 4),
				),
				'',
				invoice_total_in_finance_currency,
				invoice_total_in_finance_currency
			])

		xls_data = {
			'file_name': 'KPO knjiga %s.xlsx' % year,
			'rows': data_rows,
			'pib': issuer.company.pib,
			'full_name': issuer.personal_data.full_name(),
			'company_name': issuer.company.name,
			'company_address': issuer.company.address,
			'reg_no': issuer.company.reg_no,
			'company_activity_code': issuer.company.activity_code,
		}
		return xls_data

	@classmethod
	def get_all_years(cls):
		all_years = []
		for inv in cls.objects.all():
			couple = [inv.invoice_date.year, inv.invoice_date.year]
			if couple not in all_years:
				all_years.append(couple)

		return all_years

	@classmethod
	def get_invoice_payment(cls, invoice_id):
		invoice = cls.objects.get(id=invoice_id)
		return cls.get_payment(invoice.id).id

	@classmethod
	def get_payment_report(cls, invoice_id):
		invoice = cls.objects.get(id=invoice_id)
		invoice_items = InvoiceItem.objects.filter(**{'invoice__id': invoice_id})
		issuer_company = invoice.customer.issuer.company
		issuer_company_bank = CompanyBank.objects.filter(
			**{'company__id': issuer_company.id}
		)[0]
		issuer_bank = issuer_company_bank.bank
		issuer_bank_account = CompanyBankAccount.objects.filter(
			**{'company_bank__id': issuer_company_bank.id}
		)[0]

		customer_company = invoice.customer.company
		try:
			issuer_email = Email.objects.get(
				personal_data_id=invoice.customer.issuer.personal_data.id
			).decrypt().email_enc
		except:
			issuer_email = ''

		try:
			issuer_phone = Phone.objects.get(
				personal_data_id=invoice.customer.issuer.personal_data.id
			).phone_enc
		except:
			issuer_phone = ''

		issuer_personal = PersonalData.objects.get(
			id=invoice.customer.issuer.personal_data.id
		)

		invoice_total, currency, finance_currency_relation = cls.get_total(
			invoice.id
		)

		payment = cls.get_payment(invoice.id)

		if (
			not payment.currency_date or
			not payment.signature_date or
			not payment.payment_code
		):
			return None

		invoice_data = {
			'invoice_number': invoice.invoice_number,

			'comitent_pt_1': "%s %s" % (
				issuer_company.bank_account_id,
				issuer_company.name_pt1,
			),
			'comitent_pt_2': issuer_company.name_pt2,
			'date_of_payment': payment.date_added.strftime("%d.%m.%Y"),
			'bank_payment_id': payment.transaction_info,
			'invoice_total_in_origin_currency': "%s %s" % (
				"{:,}".format(round(invoice_total, 2)),
				currency
			),
			'currency_date': payment.currency_date.strftime("%d.%m.%Y"),
			'payer_pt_1': "%s %s" % (
				customer_company.bank_account_id,
				customer_company.name_pt1,),
			'payer_pt_2': customer_company.name_pt2,
			'reference': 'INVOICE NUMBER: %s' % invoice.invoice_number,
			'invoice_order_number': invoice.number,

			'payment_reference_code': payment.payment_code.code,
			'payment_reference_description': payment.payment_code.description,

			'signature_city': payment.signature_city,
			'signature_date': payment.signature_date.strftime("%d.%m.%Y"),

		}
		return invoice_data

	@classmethod
	def get_data_for_print(cls, invoice_id):
		invoice = cls.objects.get(id=invoice_id)
		invoice_items = InvoiceItem.objects.filter(
			**{'invoice__id': invoice_id}
		)
		issuer_company = invoice.customer.issuer.company
		issuer_company_bank = CompanyBank.objects.filter(
			**{'company__id': issuer_company.id}
		)[0]
		issuer_bank = issuer_company_bank.bank
		issuer_bank_account = CompanyBankAccount.objects.filter(
			**{'company_bank__id': issuer_company_bank.id}
		)[0]
		# import pdb;pdb.set_trace()
		customer_company = invoice.customer.company
		try:
			issuer_email = Email.objects.get(
				personal_data_id=invoice.customer.issuer.personal_data.id
			).decrypt().email_enc
		except:
			issuer_email = ''

		try:
			issuer_phone = Phone.objects.get(
				personal_data_id=invoice.customer.issuer.personal_data.id
			).phone_enc
		except:
			issuer_phone = ''
		issuer_personal = PersonalData.objects.get(
			id=invoice.customer.issuer.personal_data.id
		)

		invoice_data = {}
		invoice_data['invoice_number'] = invoice.invoice_number
		invoice_data['invoice_date'] = invoice.invoice_date
		invoice_data['due_date'] = invoice.due_date
		invoice_data['agreement_date'] = invoice.customer.\
			agreement_date.strftime("%d.%m.%Y")

		invoice_data['issuer_company'] = issuer_company.name
		invoice_data['issuer_address'] = issuer_company.address
		invoice_data['issuer_city'] = issuer_company.city.name
		invoice_data['issuer_country'] = issuer_company.country.name
		invoice_data['issuer_pib'] = issuer_company.pib
		invoice_data['issuer_apr'] = issuer_company.apr
		invoice_data['issuer_company_number'] = issuer_company.reg_no
		invoice_data['issuer_email'] = issuer_email
		invoice_data['issuer_phone'] = issuer_phone
		invoice_data['customer_company'] = customer_company.name
		invoice_data['customer_address'] = customer_company.address
		invoice_data['customer_city'] = customer_company.city.name
		invoice_data['customer_country'] = customer_company.country.name
		invoice_data['customer_pib'] = customer_company.pib

		invoice_data['invoice_items'] = []
		invoice_data['invoice_total'] = 0
		invoice_data['language_id'] = invoice.customer.invoice_language.id
		invoice_data['template'] = invoice.customer.invoice_template.location

		invoice_data['msg_text'], invoice_data['subject'] = Invoice.\
			get_email_content(invoice)

		for item in invoice_items:
			currency = item.order.bundle_asset_price.\
				asset_price.currency.identifier
			invoice_data['invoice_items'].append([
				item.order.bundle_asset_price.asset_price.asset.name + ' %s - %s' % (
					(invoice.invoice_date - datetime.timedelta(
						days=invoice.invoice_date.day - 1
					)).strftime("%d.%m.%Y"),
					invoice.invoice_date.strftime("%d.%m.%Y")
				),
				'%s %s' % (round(Order.get_price(item.order, 1), 2), currency),
				item.order.quantity, '0', '%s %s' % (round(item.order.total, 2), currency)
			])
			invoice_data['invoice_total'] += item.order.total
		invoice_data['invoice_total'] = '%s %s' % (
			round(invoice_data['invoice_total'], 2),
			currency,
		)
		invoice_data['invoice_subtotal'] = invoice_data['invoice_total']
		invoice_data['invoice_currency'] = currency

		invoice_data['bank_name'] = issuer_bank.name
		invoice_data['bank_address'] = issuer_bank.address
		invoice_data['bank_city'] = "%s %s" % (
			issuer_bank.zip_code,
			issuer_bank.city.name
		)

		invoice_data['bank_account_number'] = issuer_bank_account.account_number
		invoice_data['bank_account_payment_info'] = []
		if issuer_bank_account.swift:
			invoice_data['bank_account_payment_info'].append(issuer_bank_account.swift)
		if issuer_bank_account.iban:
			invoice_data['bank_account_payment_info'].append(issuer_bank_account.iban)
		if issuer_bank_account.chips_uid:
			invoice_data['bank_account_payment_info'].append(
				issuer_bank_account.chips_uid
			)
		if issuer_bank_account.aba:
			invoice_data['bank_account_payment_info'].append(issuer_bank_account.aba)

		return invoice_data

	@classmethod
	def get_email_content(cls, invoice):
		subject = "Faktura %s %s" % (
			invoice.invoice_number,
			invoice.invoice_date.strftime("%d.%m.%Y"),
		)
		msg_text = "Poštovani, u prilogu je faktura %s, datum %s.\n\nS' \
		poštovanjem\n%s" % (
			invoice.invoice_number,
			invoice.invoice_date.strftime("%d.%m.%Y"),
			invoice.customer.issuer.personal_data.full_name()
		)
		return msg_text, subject

	@classmethod
	def get_invoices_for_greed(cls, request, querry_filter):
		gv_name = 'Invoices'

		rows = []
		all_ivoices = InvoiceItem.objects.all()
		x = []
		for item in all_ivoices:
			if item.invoice.id in x:
				continue
			rows.append([
				item.invoice.id,
				item.invoice.invoice_number,
				round(InvoiceItem.objects.filter(
					invoice__id=item.invoice.id
				).aggregate(Sum('order__total'))['order__total__sum'], 2),
				item.order.bundle_asset_price.asset_price.currency.identifier,
				item.invoice.customer.company.name,
				item.invoice.invoice_date, item.invoice.due_date,
			])
			x.append(item.invoice.id)

		actions = permissions.filter_grid_actions(request, [

			[
				gui.grid_action(
					request,
					"<i class='fas fa-eye' style='font-size:24px'></i>",
					[
						gv_name,
						'/invoices/<int:invoice_id>/',
						'<int:invoice_id>',
						'0',
						'Please select grid value!',
						'Invoice'
					]),
				permissions.allow_any
			],
			[
				gui.grid_action(
					request,
					"<i class='fas fa-angle-double-down' style='font-size:24px'></i>",
					[
						gv_name,
						'/invoices/<int:invoice_id>/invoice/download/',
						'<int:invoice_id>',
						'0',
						'Please select grid value!',
						'Invoice'
					]),
				permissions.allow_any
			],
			[
				gui.grid_action(
					request,
					"<i class='fas fa-paper-plane' style='font-size:24px'></i>",
					[
						gv_name, '/invoices/send/<int:invoice_id>/', '<int:invoice_id>',
						'0',
						'Please select grid value!',
						'Invoice'
					]),
				permissions.allow_any
			],
			[
				gui.grid_action(
					request,
					"<i class='fas fa-eye' style='font-size:24px'></i>",
					[
						gv_name,
						'/invoices/report/<int:invoice_id>/',
						'<int:invoice_id>',
						'0',
						'Please select grid value!',
						'Bank report'
					]
				),
				permissions.allow_any
			],
			[
				gui.grid_action(
					request,
					"<i class='fas fa-angle-double-down' style='font-size:24px'></i>",
					[
						gv_name,
						'/invoices/<int:invoice_id>/report/download/', '<int:invoice_id>',
						'0',
						'Please select grid value!',
						'Bank report'
					]
				),
				permissions.allow_any
			],
			[
				gui.grid_action(
					request,
					"<i class='fas fa-edit' style='font-size:24px'></i>",
					[
						gv_name,
						'/invoices/<int:invoice_id>/payment/change/',
						'<int:invoice_id>',
						'0',
						'Please select grid value!',
						'Payment'
					]
				),
				permissions.allow_any
			],


		]), ['Invoice', 'Bank report', 'Payment']
		headers = [
			'ID', 'Invoice number', "Amount", "Currency",
			'Customer', "Invoice Date", "Due Date"
		]
		# import pdb; pdb.set_trace()
		formated = rows
		return gv_name, formated, headers, actions

	@classmethod
	def get_next_inv_number(cls, assets):
		invoice_type = InvoiceType.objects.all()[0]
		invoice_date = None
		for a in assets:
			if not invoice_date:
				invoice_date = a.valid_from
			if a.valid_from > invoice_date:
				invoice_date = a.valid_from

		year = invoice_date.year
		month_days = calendar.monthrange(invoice_date.year, invoice_date.month)[1]
		invoice_date = datetime.datetime(
			invoice_date.year, invoice_date.month, month_days
		).date()

		try:
			new_number = Invoice.objects.filter(**{
				'invoice_type__identifier': invoice_type.identifier,
				'invoice_date__contains': year,
			}).latest('number').number
			new_number += 1
		except Exception as e:
			new_number = 1
		invoice_number = '%s-%s-%s' % (invoice_type.identifier, new_number, year)
		return new_number, invoice_date, invoice_type, invoice_number

	def __str__(self):
		invoice_total, currency, currency_value = self.get_total(self.id)
		return "%s %s %s %s" % (
			self.invoice_number, invoice_total,
			currency, self.customer.company.name
		)


class Order(models.Model):
	id = models.AutoField(primary_key=True)
	bundle_asset_price = models.ForeignKey(
		BundleAssetPrice, on_delete=models.CASCADE
	)
	quantity = models.IntegerField()
	total = models.DecimalField(
		default=0,
		decimal_places=15,
		max_digits=30
	)
	date_added = models.DateTimeField(auto_now_add=True)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

	@classmethod
	def save_order_item(cls, request, customer_id, frm):
		order = Order()
		order.bundle_asset_price = BundleAssetPrice.objects.get(
			id=frm.cleaned_data['id']
		)
		order.customer = Customer.objects.get(id=customer_id)
		order.quantity = frm.cleaned_data['quantity']
		order.save()

	@classmethod
	def get_customer_orders(cls, request, customer_id, info=False):

		paid_order_ids = InvoiceItem.objects.filter(
			**{'order__customer__id': customer_id}
		).values_list('order__id')
		orders = (cls.objects.filter(
			**{'customer__id': customer_id, }
		).exclude(id__in=paid_order_ids).values_list(
			"id", "quantity",
			"bundle_asset_price__asset_price__asset__name",
			'total',
			'bundle_asset_price__asset_price__currency__identifier'
		)
		)
		if not info:
			return [[v, y + (' x %s pieces' % x), z] for v, x, y, z, m in orders]
		else:
			info_items = []
			for v, x, y, z, m in orders:
				info_item = "%s %s %s" % (y + (' x %s pieces' % x), z, m)
				info_items.append(info_item)

			return info_items

	def save(self, *args, **kwargs):
		if not self.id:
			self.total = Order.get_price(self, self.quantity)
		super(Order, self).save(*args, **kwargs)

	@classmethod
	def get_price(cls, order, quantity):
		if order.bundle_asset_price.discount.fixed_price:
			price = quantity * order.bundle_asset_price.discount.fixed_price
		else:
			price = (quantity * order.bundle_asset_price.asset_price.price)
			if order.bundle_asset_price.discount.percent:
				price = price - price * (
					order.bundle_asset_price.discount.percent / 100
				)
			if order.bundle_asset_price.discount.fixed_discount:
				price = price - order.bundle_asset_price.discount.fixed_discount

		return price

	def __str__(self):
		return "%s x %s %s %s %s" % (
			self.quantity,
			self.bundle_asset_price.asset_price.asset.__str__(),
			self.bundle_asset_price.bundle.__str__(), self.total,
			self.bundle_asset_price.asset_price.currency.identifier)


class InvoiceItem(models.Model):
	id = models.AutoField(primary_key=True)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

	def __str__(self):
		return "%s %s" % (self.invoice.invoice_number, self.order.__str__())


class PaymentProcessor(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200)

	def __str__(self):
		return self.name


class Payment(models.Model):
	id = models.AutoField(primary_key=True)
	paid_amount = models.DecimalField(default=0, decimal_places=15, max_digits=30)
	refund_part = models.DecimalField(default=0, decimal_places=15, max_digits=30)
	tax_part = models.DecimalField(default=0, decimal_places=15, max_digits=30)
	customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
	currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
	payment_processor = models.ForeignKey(
		PaymentProcessor,
		on_delete=models.CASCADE
	)
	currency_date = models.DateField(blank=True, null=True)
	transaction_info = models.CharField(max_length=100, blank=True)
	signature_city = models.CharField(max_length=100, blank=True, null=True)
	signature_date = models.DateField(blank=True, null=True)
	payment_code = models.ForeignKey(
		PaymenCode,
		on_delete=models.CASCADE,
		blank=True,
		null=True
	)
	date_added = models.DateField()

	@classmethod
	def save_payment_and_orders(cls, request, customer_id, frm, orders):
		payment = Payment()
		payment.payment_processor = PaymentProcessor.objects.get(
			id=frm.cleaned_data['payment_processor'])
		payment.currency = Currency.objects.get(id=frm.cleaned_data['currency'])
		payment.customer = Customer.objects.get(id=customer_id)
		payment.paid_amount = frm.cleaned_data['total']
		payment.date_added = datetime.datetime.now().date()

		customer = Customer.objects.get(id=customer_id)

		order_models = []
		for id, name, price in orders:
			order = Order.objects.get(id=id)

			orderpayment = OrderPayment()
			orderpayment.order = order
			orderpayment.paid_amount = frm.cleaned_data[str(id)]

			assets = []

			if order.bundle_asset_price.asset_price.asset.allow_multiple:
				assets_count = order.quantity
			else:
				assets_count = 1

			for x in range(assets_count):
				customerasset = CustomerAsset()
				customerasset.customer = customer
				customerasset.asset = order.bundle_asset_price.asset_price.asset
				customerasset.order = order
				assets.append(customerasset)

			order_models.append([order, orderpayment, assets])

		with transaction.atomic():
			payment.save()

			for order, o_payment, c_assets in order_models:
				o_payment.payment = payment
				o_payment.save()

				for c_asset in c_assets:
					v_from, v_to = CustomerAsset.get_next_asset_duration(
						customer_id,
						order.bundle_asset_price.asset_price.asset.id,
						order.bundle_asset_price.asset_price.duration.id,
					)
					c_asset.valid_from = v_from
					c_asset.valid_to = v_to
					c_asset.save()

		Payment.make_invoice(orders, customer_id, assets)

	@classmethod
	def make_invoice(cls, orders, customer_id, assets):
		invoice = Invoice()
		invoice.customer_id = customer_id
		invoice.number, invoice.invoice_date, invoice.invoice_type, \
			invoice.invoice_number = Invoice.get_next_inv_number(assets)
		invoice.due_date = invoice.invoice_date + datetime.timedelta(days=15)
		invoice.year = invoice.invoice_date.year
		i_items = []
		for id, name, price in orders:
			order = Order.objects.get(id=id)
			invoiceitem = InvoiceItem()
			invoiceitem.order = Order.objects.get(id=id)

			i_items.append(invoiceitem)

		with transaction.atomic():
			invoice.save()

			for i_item in i_items:
				i_item.invoice = invoice
				i_item.save()

	def __str__(self):
		return "%s %s %s" % (
			self.paid_amount, self.currency.identifier, self.date_added
		)


class OrderPayment(models.Model):
	id = models.AutoField(primary_key=True)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
	paid_amount = models.DecimalField(
		default=0,
		decimal_places=15,
		max_digits=30
	)

	def __str__(self):
		return "%s %s" % (self.payment.paid_amount, self.payment.currency.identifier)


class CustomerAsset(models.Model):
	id = models.AutoField(primary_key=True)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	asset = models.ForeignKey(
		Asset, related_name='asset', on_delete=models.CASCADE
	)
	valid_from = models.DateTimeField()
	valid_to = models.DateTimeField(null=True)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	origin_asset = models.ForeignKey(
		Asset, related_name='origin_asset', null=True,
		on_delete=models.CASCADE, blank=True
	)

	@classmethod
	def get_next_asset_duration(cls, customer_id, asset_id, duration_id):
		no_months = Duration.objects.get(id=duration_id).no_months
		no_days = Duration.objects.get(id=duration_id).no_days
		no_seconds = Duration.objects.get(id=duration_id).no_seconds

		try:
			max_valid_to = CustomerAsset.objects.filter(
				**{'customer__id': customer_id, 'asset__id': asset_id}
			).latest('valid_to').valid_to
			if not max_valid_to:
				max_valid_to = datetime.datetime.now()
		except:
			max_valid_to = datetime.datetime.now()
			max_valid_to = max_valid_to - datetime.timedelta(days=max_valid_to.day)

		v_from = max_valid_to + datetime.timedelta(days=1)
		v_from = datetime.datetime(v_from.year, v_from.month, v_from.day)
		v_to = v_from

		if no_months:
			v_to = operations.\
				add_months_to_date(v_from, no_months) - datetime.timedelta(seconds=1)
		elif no_days:
			v_to = v_to + datetime.timedelta(days=no_days + 1)
			v_to = v_to - datetime.timedelta(seconds=1)
		elif no_seconds:
			v_to = v_to + datetime.timedelta(seconds=no_seconds)
		else:
			v_to = None

		return v_from, v_to

	@classmethod
	def format_customer_assets_for_greed(cls, request, querry_filter):
		gv_name = 'CustomerAssets'
		rows = cls.objects.filter(**querry_filter).values_list(
			'id', 'asset__name',
			'order__bundle_asset_price__asset_price__duration__name',
			'valid_from', 'valid_to'
		)
		actions = permissions.filter_grid_actions(request, [
		]), []
		headers = ['ID', 'Name', "Duration", "Valid from", "Valid to"]
		formated = rows
		return gv_name, formated, headers, actions

	def __str__(self):
		return "%s %s %s %s" % (
			self.customer,
			self.asset,
			self.valid_from,
			self.valid_to
		)
