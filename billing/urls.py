"""company URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from billing import views

urlpatterns = [
	path('', views.home, name='home'),
	path(r'login/', views.login, name='login'),
	path(r'about/', views.about, name='about'),
	path(
		r'invoices/<int:invoice_id>/report/download/',
		views.download_payment_report,
		name='download_payment_report'
	),
	path(
		r'invoices/<int:invoice_id>/invoice/download/',
		views.download_invoice,
		name='download_invoice'),
	path(
		r'invoices/<int:invoice_id>/payment/change/',
		views.invoice_payment_change, name='invoice_payment_change'
	),
	path(
		r'invoices/report/<int:invoice_id>/',
		views.invoice_payment_report,
		name='invoice_payment_report'
	),
	path(
		r'invoices/send/<int:invoice_id>/',
		views.send_invoice,
		name='send_invoice'
	),
	path(
		r'invoices/<int:invoice_id>/',
		views.view_invoice,
		name='view_invoice'
	),
	path(
		r'invoices/',
		views.invoices,
		name='invoices'
	),
	path(
		r'customers/<int:customer_id>/assets/',
		views.customer_assets,
		name='customer_assets'
	),
	path(
		r'customers/<int:customer_id>/offers/',
		views.customer_offers,
		name='customer_offers'
	),
	path(
		r'customers/<int:customer_id>/cart/',
		views.customer_cart,
		name='customer_cart'
	),
	path(
		r'customers/',
		views.customers,
		name='customers'
	),
	path(
		r'kpo/download/<int:year>/',
		views.download_kpo,
		name='download_kpo'
	),
	path(
		r'kpo/',
		views.kpo,
		name='kpo'
	),
	path(
		r'db/',
		views.download_db,
		name='db'
	),
	path(
		r'logout/',
		views.logout_user,
		name='logout'
	),
]
