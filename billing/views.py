from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string, get_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login as django_login
from django.conf import settings
import billing.gui as gui
import billing.forms as forms
import billing.operations as operations
import billing.models as models
import billing.xls_templates as xls


def logout_user(request):
	logout(request)
	return redirect('login')


def about(request):
	context = gui.get_init_context(request)
	return render(request, "billing/about_page.html", context)


def home(request):
	if request.user.is_authenticated:
		context = gui.get_init_context(request)
		context['content_links'] = gui.get_content_links(request)
		return render(request, "billing/home.html", context)
	else:
		return redirect('login')


def login(request):
	if request.user.is_authenticated:
		return redirect('home')

	context = gui.get_init_context(request)
	if request.POST:
		context['main_form'] = forms.LoginForm(request.POST, request=request)

		if context['main_form'].is_valid():
			user = authenticate(
				username=request.POST['username'],
				password=request.POST['password']
			)
			if user:
				django_login(request, user)
				return redirect('home')

			else:
				context['main_form'].add_error(None, "Incorect credentials")

	else:
		context['main_form'] = forms.LoginForm()

	return render(request, "billing/main_form.html", context)


@login_required(login_url='/login/')
def customer_assets(request, customer_id):
	context = gui.get_init_context(request)

	gv_name, rows, headers, actions = \
		models.CustomerAsset.\
		format_customer_assets_for_greed(request, {'customer__id': customer_id})

	context['dg_data'] = gui.setup_dataview(gv_name, rows, headers, actions)

	return render(request, "billing/datagrid_with_actions.html", context)


@login_required(login_url='/login/')
def send_invoice(request, invoice_id):
	invoice_data = models.Invoice.get_data_for_print(invoice_id)
	inv = models.Invoice.objects.get(id=invoice_id)
	try:
		customer_email = models.Email.objects.get(
			personal_data_id=inv.customer.personal_data.id
		).decrypt().email_enc
	except Exception as e:
		messages.info(request, 'Customer mail not set!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	try:
		issuer_email = models.Email.objects.get(
			personal_data_id=inv.customer.issuer.personal_data.id
		).decrypt().email_enc

		issuer_email_password = models.Email.objects.get(
			personal_data_id=inv.customer.issuer.personal_data.id
		).decrypt().email_password_enc

		issuer_name = models.Issuer.objects.get(
			id=inv.customer.issuer.id
		).personal_data.full_name()

	except Exception as e:
		messages.info(request, 'Issuer mail not set!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	if inv.is_sent:
		messages.info(request, 'Invoice Allredy sent!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	context = gui.format_invoice_data_object(
		request, invoice_data, settings.STATIC_ROOT,
		models.Translation.translate, invoice_data['language_id']
	)
	template = get_template(invoice_data['template'])
	html = template.render(context)
	p = operations.PDF(html, False)
	if p.error:
		messages.error(request, p.error)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	pdf = p.memory_file, invoice_data['invoice_number'] + '.pdf'

	credentials = issuer_email, issuer_email_password

	r, v = operations.send_doc_to_customer(
		credentials, issuer_name, invoice_data['subject'],
		invoice_data['msg_text'], [customer_email], [], [pdf]
	)

	if not r:
		messages.error(request, v)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	inv.is_sent = True
	inv.save()

	messages.info(request, 'Invoice sent to %s!' % customer_email)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/login/')
def view_invoice(request, invoice_id):
	invoice_data = models.Invoice.get_data_for_print(invoice_id)
	context = gui.format_invoice_data_object(
		request, invoice_data, settings.STATIC_URL,
		models.Translation.translate, invoice_data['language_id']
	)
	return render(request, invoice_data['template'], context)


@login_required(login_url='/login/')
def download_invoice(request, invoice_id):
	invoice_data = models.Invoice.get_data_for_print(invoice_id)

	context = gui.format_invoice_data_object(
		request, invoice_data, settings.STATIC_ROOT,
		models.Translation.translate, invoice_data['language_id']
	)
	template = get_template(invoice_data['template'])
	html = template.render(context)

	p = operations.PDF(html, False)
	if p.error:
		messages.error(request, p.error)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	response = HttpResponse(p.memory_file, content_type='application/pdf')
	response['Content-Disposition'] = \
		'attachment; filename="%s.pdf"' % invoice_data['invoice_number']
	return response


@login_required(login_url='/login/')
def download_kpo(request, year):
	xls_data = models.Invoice.get_kpo_for_year(year)

	kpo = xls.make_kpo(xls_data)
	response = HttpResponse(kpo, content_type='application/vnd.openxmlformats-\
		officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = \
		'attachment; filename="%s"' % xls_data['file_name']
	return response


@login_required(login_url='/login/')
def download_payment_report(request, invoice_id):
	invoice_data = models.Invoice.get_payment_report(invoice_id)
	if not invoice_data:
		messages.info(request, 'Payment not complete for report!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	context = gui.format_invoice_payment_report_data_object(
		invoice_data,
		settings.STATIC_ROOT
	)
	template = get_template('billing/bank_payment_report.html')
	html = template.render(context)

	p = operations.PDF(html, False)
	if p.error:
		messages.error(request, p.error)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	response = HttpResponse(p.memory_file, content_type='application/pdf')
	response['Content-Disposition'] = \
		'attachment; filename="payment report %s.pdf"' % \
		invoice_data['invoice_number']
	return response


@login_required(login_url='/login/')
def invoice_payment_change(request, invoice_id):
	paymnent_id = models.Invoice.get_invoice_payment(invoice_id)
	return HttpResponseRedirect(
		reverse('admin:billing_payment_change', args=(paymnent_id,))
	)


@login_required(login_url='/login/')
def invoice_payment_report(request, invoice_id):
	invoice_data = models.Invoice.get_payment_report(invoice_id)
	if not invoice_data:
		messages.info(request, 'Payment not complete for report!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	context = gui.format_invoice_payment_report_data_object(
		invoice_data, settings.STATIC_URL
	)
	return render(request, "billing/bank_payment_report.html", context)


@login_required(login_url='/login/')
def customer_cart(request, customer_id):
	context = gui.get_init_context(request)
	orders = models.Order.get_customer_orders(request, customer_id)
	if request.POST:
		context['main_form'] = forms.PaymentForm(
			request.POST, request=request,
			customer_id=customer_id, orders=orders
		)

		if context['main_form'].is_valid():
			models.Payment.save_payment_and_orders(
				request, customer_id,
				context['main_form'], orders
			)
			return redirect('customer_assets', customer_id=customer_id)

	else:
		context['main_form'] = forms.PaymentForm(
			request=request, customer_id=customer_id, orders=orders
		)

	return render(request, "billing/main_form.html", context)


@login_required(login_url='/login/')
def customer_offers(request, customer_id):
	context = gui.get_init_context(request)
	context['cart_items'] = models.Order.get_customer_orders(
		request, customer_id, info=True
	)

	if request.POST:
		context['offer_item_forms'], submited_frm = gui.get_forms_list(
			request, models.BundleAssetPrice.get_available_bundles(request),
			forms.OrderItemForm
		)

		if submited_frm:
			if submited_frm.is_valid():
				models.Order.save_order_item(request, customer_id, submited_frm)

			context['cart_items'] = models.Order.get_customer_orders(
				request, customer_id, info=True
			)
			context['main_offers_form'] = forms.OffersForm()
		else:
			context['main_offers_form'] = forms.OffersForm(
				request.POST, request=request,
				orders=models.Order.get_customer_orders(request, customer_id)
			)
			if context['main_offers_form'].is_valid():
				return redirect('customer_cart', customer_id=customer_id)
	else:
		context['offer_item_forms'], submited_frm = gui.get_forms_list(
			request, models.BundleAssetPrice.get_available_bundles(request),
			forms.OrderItemForm
		)
		context['main_offers_form'] = forms.OffersForm()

	return render(request, "billing/offers.html", context)


@login_required(login_url='/login/')
def customers(request):
	context = gui.get_init_context(request)

	context['filter_form'] = forms.SearchCustomersForm(
		request.GET, request=request
	)
	if context['filter_form'].is_valid():
		gv_name, rows, headers, actions = \
			models.Customer.\
			format_customer_company_for_greed(
				request,
				context['filter_form'].querry_filter
			)

		context['dg_data'] = gui.setup_dataview(gv_name, rows, headers, actions)

	return render(request, "billing/datagrid_with_actions.html", context)


@login_required(login_url='/login/')
def invoices(request):
	context = gui.get_init_context(request)

	gv_name, rows, headers, actions = \
		models.Invoice.get_invoices_for_greed(request, {})

	context['dg_data'] = gui.setup_dataview(gv_name, rows, headers, actions)

	return render(request, "billing/datagrid_with_actions.html", context)


@login_required(login_url='/login/')
def kpo(request):
	context = gui.get_init_context(request)
	years = models.Invoice.get_all_years()

	if request.POST:
		context['main_form'] = forms.KPOForm(
			request.POST, request=request, years=years
		)
		if context['main_form'].is_valid():
			return redirect(
				'download_kpo',
				year=context['main_form'].cleaned_data['year']
			)
	else:
		context['main_form'] = forms.KPOForm(request=request, years=years)

	return render(request, "billing/main_form.html", context)
