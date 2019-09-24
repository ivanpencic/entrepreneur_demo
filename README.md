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