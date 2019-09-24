from django import forms
from django.core.exceptions import ValidationError
import billing.models as models


class Base(forms.Form):
	METHOD = 'GET'
	querry_filter = {}
	action = ''
	form_id = forms.CharField(
		widget=forms.HiddenInput(), required=False, initial='default'
	)

	def add_to_filter(
		self, join_tables, db_field, form_field, custom_operator=None
	):
		querry = '__'.join(join_tables)
		if querry:
			querry += '__'

		querry += db_field

		if custom_operator:
			querry += ('__%s' % custom_operator)

		self.querry_filter[querry] = self.cleaned_data[form_field]

	def check_positive(self, num):
		if num < 0:
			raise ValidationError('Negative numbers not allowed!')

	def check_number(self, field):
		data = getattr(self.request, getattr(self, 'METHOD'))
		if data.get('csrfmiddlewaretoken', None):
			try:
				if data.get(field, None):
					int(self.cleaned_data[field])
			except:
				raise ValidationError('Number required')

	def check_criteria_presence(self):
		data = getattr(self.request, getattr(self, 'METHOD'))
		if data.get('csrfmiddlewaretoken', None):
			criteria = False
			for key in self.fields:

				if data.get(key, None):
					criteria = True
					break

			if not criteria:
				raise ValidationError("No criteria")


class OffersForm(Base):
	method = "POST"
	submit_label = "Save offers"

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		self.orders = kwargs.pop('orders', None)
		super(OffersForm, self).__init__(*args, **kwargs)

	def clean(self):
		if not len(self.orders):
			raise ValidationError("No offers submited")


class KPOForm(Base):
	method = "POST"
	submit_label = "Download KPO"

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		self.years = kwargs.pop('years', None)
		super(KPOForm, self).__init__(*args, **kwargs)

		self.fields['year'] = forms.ChoiceField(
			choices=self.years, label="For year", required=True
		)


class PaymentForm(Base):
	method = "POST"
	submit_label = "Save payment"

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		self.customer_id = kwargs.pop('customer_id', None)
		self.orders = kwargs.pop('orders', None)
		super(PaymentForm, self).__init__(*args, **kwargs)

		total = 0
		cur_id = 0
		for id, name, price in self.orders:
			self.fields[str(id)] = forms.DecimalField(
				label=name, required=True, initial=price
			)
			total += price
			cur_id = models.Order.objects.get(
				id=id
			).bundle_asset_price.asset_price.currency.id

		self.fields['total'] = forms.DecimalField(
			label="Total", required=True, initial=total
		)

		self.fields['payment_processor'] = forms.ChoiceField(
			choices=models.PaymentProcessor.objects.all().values_list('id', 'name'),
			label="Payment Processor",
			required=True
		)
		self.fields['currency'] = forms.ChoiceField(
			choices=models.Currency.objects.all().values_list('id', 'identifier'),
			label="Currency",
			required=True)
		self.initial['currency'] = cur_id

	def clean(self):

		self.check_positive(self.cleaned_data['total'])
		total_calculated = 0
		for id, name, price in self.orders:
			self.cleaned_data[str(id)]
			total_calculated += self.cleaned_data[str(id)]
			self.check_positive(self.cleaned_data[str(id)])

		if self.cleaned_data['total'] != total_calculated:
			raise ValidationError("Enterd item sum and total do not match!")


class OrderItemForm(Base):
	id = forms.CharField(widget=forms.HiddenInput(), required=False)
	quantity = forms.IntegerField(label="", required=True, initial=1)
	method = "POST"
	submit_label = "Add"

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(OrderItemForm, self).__init__(*args, **kwargs)
		self.fields['form_id'].initial = 'order_item'

	def clean(self):
		pass


class SearchCustomersForm(Base):
	name = forms.CharField(label='Name', max_length=80, required=False)
	customer_id = forms.CharField(
		label="Customer ID", max_length=20, required=False
	)

	submit_label = "Search"

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(SearchCustomersForm, self).__init__(*args, **kwargs)

	def clean_customer_id(self):
		self.check_number('customer_id')
		return self.cleaned_data['customer_id']

	def clean(self):
		self.check_criteria_presence()

		if self.cleaned_data.get('name', None):
			self.add_to_filter([], 'name', 'name', 'contains')
		if self.cleaned_data.get('customer_id', None):
			self.add_to_filter([], 'id', 'customer_id')


class LoginForm(Base):
	username = forms.CharField(label='Username', max_length=80, required=True)
	password = password = forms.CharField(
		label='Password',
		widget=forms.PasswordInput()
	)

	method = "POST"
	submit_label = "Login"

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(LoginForm, self).__init__(*args, **kwargs)
