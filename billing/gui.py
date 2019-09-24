from django.urls import reverse
from django.conf import settings

a_link = 'a_tag'
div_link = 'div_tag'
grid_link = 'js_function_link'


def get_init_context(request):
	context = {
		'top_links': get_top_links(request),
		'app_version': settings.VER,
		'about': get_about(),
	}
	return context


def get_about():
	return [
		['#Description', [
			"- Purpose of this app is to have simple enterprainer CRM for documenting invoices, customers, payments and reports",
			"- App is adopted for Serbian enterprainer laws(export KPO xls report for year)",
			"- App has basic functionalities like add customer subscription, add customers payment, make invoice, view invoice, download invoice PDF, email invoice(needs issuer email and password and customers email which will be enctypted), make KPO XLS report for year, make bank report for non native payment",
			"- Some data like names, phones and emails are AES encrypted",
		]
		],
		['#Technical requirements', [
			"- python 3+",
			"- Wkhtmltopdf binary needs to be installed for making PDF-s, binary path is in settings variable WKHTML_BIN_PATH (on Heroku install is done through buildpacks)",
			"- Install python pip",
			"- Install pipenv (environment tool like virtualenv) 'pip install pipenv' this step may fail on missing dev libs (python-dev libmysqlclient-dev openssl openssl-dev pycrypto etc..)",
			"- Install python requirements 'pipenv install' to install all external python libs",
			"- Start test server if DB is ready (by default demo.db is ready for usage) 'pipenv run python manage.py runserver 127.0.0.0:8000'",
		]
		],
		['#Demo DB preview', [
			"- Example default database is sqlite demo.db filled with all required data for demo puropose. Demo login is u:admin p:8888 (heroku resets this DB file periodicly)",
		]
		],
		['#Blanc DB setup', [
			"- run 'pipenv run python manage.py migrate' to create all db tables",
			"- run 'pipenv run python manage.py createsuperuser' to create first superuser",
			"- Login with superuser and insert necessary models with Django admin app at address admin/billing/ (almost all tables and relations needs to be filled)",
		]
		],
		['#Usage workflow', [
			"- After app data is up and running",
			"- Go to customers select one from list and add asset '+' icon, next you choose asset and quantity or multiple assets, then insert payment details (no matter if not receved yet)",
			"- After saving customer gets subscription (with duration if type is not permanent), invoice record is also inserted",
			"- Customers assets can be seen from customers page, select customer and click list icon action link",
			"- Now you can go from homepage to invoices and preview or download invoice or email it to customers predefined email",
			"- Bank report is for non native currency payments when you need to send report to bank about recived payment",
			"- When you recive non native currency payment you must update payment record with currency date, date of reciving and transaction info so that bank report can be made",
			"- For bank report transparent PNG signature must be replaced company/billing/static/billing/img/payment_report/signature.png",
			"- For non native currency invoices currency relation should be filled for KPO report (URL admin/billing/currency/)",
			"- KPO report can be exported as xls for defined year (years are populated by existing invoice dates)",
			"- Invoice translation can be done on url admin/billing/translation/ for language defined as customers invoice language",
		]
		],
		['#Customization', [
			"- For invoice logo customization replace company/billing/static/billing/img/logo/full_logo.png ",
			"- For app home logo customization replace company/billing/static/billing/img/logo/part_logo.png ",
			"- For web app icon customization replace company/billing/static/billing/img/logo/logo_icon.ico ",
		]
		],
		['#Notices', [
			"- Currently only Credit Agricole bank report html template is available",
			"- All foreign keys set to cascade! Carefull when deleting rows, all relations will be deleted!",
			"- Not optimised for hight traffic(not tested)!",
			"- Tested on Heroku free hosting",
			"- Default language_id is set to 1 change if needed",
			"- For sending invoice to client, currently, email must be sent from gmail and 'Allow less secure apps to access your Gmail account' must be enabled",
		]
		],
	]


def get_content_links(request):
	links = [
		["Invoices<br><br><i class='fas fa-file-invoice-dollar' \
			style='font-size:48px'></i>", reverse("invoices"), a_link],
		["Customeres<br><br><i class='fas fa-users' \
			style='font-size:48px'></i>", reverse("customers"), a_link],
		["KPO<br><br><i class='fas fa-file-excel' \
			style='font-size:48px'></i>", reverse("kpo"), a_link],
	]

	return format_base_links(links)


def format_base_links(links):
	formated = []
	for x in links:
		name, url, u_type = x
		formated.append({'name': name, 'url': url, 'type': u_type})
	return formated


def grid_action(request, name, url_data):
	return [name, url_data, grid_link]


def get_forms_list(request, items, form_class):
	formated = []
	submited_frm = None
	for id, name in items:
		if request.POST.get('form_id', None) == 'order_item':
			if request.POST and str(id) == str(request.POST['id']):
				frm = form_class(request.POST, request=request)
				submited_frm = frm
			else:
				frm = form_class()

		else:
			frm = form_class()

		frm.fields['quantity'].label = name
		frm.fields['id'].initial = id
		formated.append(frm)

	return formated, submited_frm


def get_top_links(request):
	if request.user.is_authenticated:
		log_link = ["Logout", reverse("logout"), a_link]
	else:
		log_link = ["Login", reverse("login"), a_link]

	links = [
		["Home", reverse("home"), a_link],
		["Admin", "/admin", a_link],
		["About", "/about", a_link],
		log_link,
	]

	return format_base_links(links)


def setup_dataview(name, rows, headers, actions):
	return {
		'name': name,
		'headers': headers,
		'rows': rows,
		'actions': [format_base_links(actions[0]), actions[1]],
	}


def format_invoice_payment_report_data_object(invoice_data, static_part):
	# static_part can be url when veiwing inv as html or full filesystem
	# path when pdfkit looking for static files
	if static_part[-1] != '/':
		static_part += '/'

	context = {
		'background_src': static_part + "billing/img/payment_report/background.jpg",
		'signature_url': static_part + 'billing/img/payment_report/signature.png',
	}
	context.update(invoice_data)

	return context


def format_invoice_data_object(
	request, invoice_data, static_part, translate, language_id
):
	# print(translate(request, 'text', language_id))
	# static_part can be url when veiwing inv as html or full filesystem path
	# when pdfkit looking for static files
	if static_part[-1] != '/':
		static_part += '/'

	right_head_up = [
		translate(
			request, 'Invoice number: %s', language_id
		) % invoice_data['invoice_number'],
		translate(
			request, 'Invoice date: %s', language_id
		) % invoice_data['invoice_date'],
		translate(
			request, 'Due date: %s', language_id
		) % invoice_data['due_date'],
	]

	left_head_down = [
		invoice_data['issuer_company'],
		invoice_data['issuer_address'],
		'%s, %s' % (invoice_data['issuer_city'], translate(
			request, invoice_data['issuer_country'], language_id
		)),
		translate(request, 'VAT: %s', language_id) % invoice_data['issuer_pib'],
		translate(
			request, 'Registration number: %s', language_id
		) % invoice_data['issuer_company_number'],
	]

	right_head_down = [
		invoice_data['customer_company'],
		invoice_data['customer_address'],
		'%s, %s' % (invoice_data['customer_city'], translate(
			request, invoice_data['customer_country'], language_id
		)),
		translate(
			request, 'VAT: %s', language_id
		) % invoice_data['customer_pib'],
	]

	items_headers = [
		translate(request, 'Service description', language_id),
		translate(request, 'Price', language_id),
		translate(request, 'Quantity', language_id),
		translate(request, 'Discount', language_id),
		translate(request, 'Amount', language_id),
	]
	items_rows = []
	for itm in invoice_data['invoice_items']:
		desctiption, piece_price, quantity, discount, total = itm
		items_rows.append([desctiption, piece_price, quantity, discount, total])

	total = translate(
		request, 'Invoice Total: %s', language_id
	) % invoice_data['invoice_total']
	subtotal = translate(
		request, 'Subtotal: %s', language_id
	) % invoice_data['invoice_subtotal']
	vat_amount = translate(
		request, 'VAT rate 0%%:     0 %s', language_id
	) % invoice_data['invoice_currency']

	footer_left = [
		translate(request, 'Payment instructions:', language_id),
		invoice_data['bank_name'],
		invoice_data['bank_address'],
		invoice_data['bank_city'],
		translate(
			request, 'Account number: %s', language_id
		) % invoice_data['bank_account_number'],
	]
	footer_left.extend(invoice_data['bank_account_payment_info'])
	footer_left.extend([
		'',
		'',
		translate(
			request,
			'*Invoice is valid without stamp and signature',
			language_id
		),
		translate(
			request,
			'*Enterpreneur is not in VAT system',
			language_id
		),
	])

	footer_right = [
		translate(request, 'Contact info:', language_id),
		'Email: %s' % invoice_data['issuer_email'],
		translate(request, 'Phone: %s', language_id) % invoice_data['issuer_phone'],
	]

	context = {
		'logo_src': static_part + "billing/img/logo/full_logo.png",
		'right_head_up': right_head_up,
		'left_head_down': left_head_down,
		'right_head_down': right_head_down,
		'items_headers': items_headers,
		'items_rows': items_rows,
		'total': total,
		'subtotal': subtotal,
		'invoice_topic': translate(
			request,
			'IT services according to cooperation agreement dated %s', language_id
		) % invoice_data['agreement_date'],
		'vat_amount': vat_amount,
		'footer_left': footer_left,
		'footer_right': footer_right,
	}

	return context
