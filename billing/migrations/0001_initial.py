# Generated by Django 2.0.6 on 2019-06-15 16:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('allow_multiple', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='AssetPrice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('price', models.DecimalField(decimal_places=15, max_digits=30)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField(blank=True, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Asset')),
            ],
        ),
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('zip_code', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Bundle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BundleAssetPrice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('asset_price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.AssetPrice')),
                ('bundle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Bundle')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
                ('reg_no', models.CharField(max_length=30)),
                ('pib', models.CharField(blank=True, max_length=30)),
                ('apr', models.CharField(blank=True, max_length=30)),
                ('address', models.CharField(max_length=300)),
                ('activity_code', models.CharField(max_length=30)),
                ('name_pt1', models.CharField(blank=True, max_length=150)),
                ('name_pt2', models.CharField(blank=True, max_length=150)),
                ('bank_account_id', models.CharField(blank=True, max_length=100)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.City')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyBank',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Bank')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Company')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyBankAccount',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('account_number', models.CharField(max_length=100)),
                ('aba', models.CharField(blank=True, max_length=100, null=True)),
                ('chips_uid', models.CharField(blank=True, max_length=100, null=True)),
                ('swift', models.CharField(blank=True, max_length=100, null=True)),
                ('iban', models.CharField(blank=True, max_length=100, null=True)),
                ('company_bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.CompanyBank')),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('identifier', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CurrencyRelation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.DecimalField(decimal_places=15, max_digits=30)),
                ('relation_date', models.DateField()),
                ('from_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_currency', to='billing.Currency')),
                ('to_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_currency', to='billing.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.Company')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerAsset',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField(null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset', to='billing.Asset')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('percent', models.DecimalField(decimal_places=15, max_digits=30)),
                ('fixed_discount', models.DecimalField(decimal_places=15, default=0, max_digits=30)),
                ('fixed_price', models.DecimalField(decimal_places=15, default=0, max_digits=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('no_seconds', models.IntegerField()),
                ('no_days', models.IntegerField()),
                ('no_months', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email_enc', models.CharField(max_length=200)),
                ('email_password_enc', models.CharField(blank=True, default='', max_length=200)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('invoice_number', models.CharField(max_length=50)),
                ('number', models.IntegerField()),
                ('year', models.IntegerField()),
                ('due_date', models.DateField(null=True)),
                ('invoice_date', models.DateField()),
                ('is_sent', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('identifier', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Issuer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Company')),
                ('finance_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('total', models.DecimalField(decimal_places=15, default=0, max_digits=30)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('bundle_asset_price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.BundleAssetPrice')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('paid_amount', models.DecimalField(decimal_places=15, default=0, max_digits=30)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Order')),
            ],
        ),
        migrations.CreateModel(
            name='PaymenCode',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('paid_amount', models.DecimalField(decimal_places=15, default=0, max_digits=30)),
                ('refund_part', models.DecimalField(decimal_places=15, default=0, max_digits=30)),
                ('tax_part', models.DecimalField(decimal_places=15, default=0, max_digits=30)),
                ('currency_date', models.DateField(blank=True, null=True)),
                ('transaction_info', models.CharField(blank=True, max_length=100)),
                ('signature_city', models.CharField(blank=True, max_length=100, null=True)),
                ('signature_date', models.DateField(blank=True, null=True)),
                ('date_added', models.DateField()),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Currency')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.Customer')),
                ('payment_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.PaymenCode')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentProcessor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PersonalData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name_enc', models.CharField(max_length=80)),
                ('last_name_enc', models.CharField(max_length=80)),
                ('address_enc', models.CharField(blank=True, max_length=300)),
                ('salt', models.CharField(max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('phone_enc', models.CharField(max_length=200)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('personal_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.PersonalData')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('target_text', models.CharField(max_length=500)),
                ('Translation', models.CharField(max_length=500)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Language')),
            ],
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_processor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.PaymentProcessor'),
        ),
        migrations.AddField(
            model_name='orderpayment',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Payment'),
        ),
        migrations.AddField(
            model_name='issuer',
            name='personal_data',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.PersonalData'),
        ),
        migrations.AddField(
            model_name='issuer',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Order'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.InvoiceType'),
        ),
        migrations.AddField(
            model_name='email',
            name='personal_data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.PersonalData'),
        ),
        migrations.AlterUniqueTogether(
            name='discount',
            unique_together={('percent', 'fixed_discount', 'fixed_price')},
        ),
        migrations.AddField(
            model_name='customerasset',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Order'),
        ),
        migrations.AddField(
            model_name='customerasset',
            name='origin_asset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='origin_asset', to='billing.Asset'),
        ),
        migrations.AddField(
            model_name='customer',
            name='invoice_language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Language'),
        ),
        migrations.AddField(
            model_name='customer',
            name='invoice_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Template'),
        ),
        migrations.AddField(
            model_name='customer',
            name='issuer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Issuer'),
        ),
        migrations.AddField(
            model_name='customer',
            name='personal_data',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.PersonalData'),
        ),
        migrations.AddField(
            model_name='customer',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='companybankaccount',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Currency'),
        ),
        migrations.AddField(
            model_name='company',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Country'),
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Country'),
        ),
        migrations.AddField(
            model_name='bundleassetprice',
            name='discount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Discount'),
        ),
        migrations.AddField(
            model_name='bundleassetprice',
            name='issuer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Issuer'),
        ),
        migrations.AddField(
            model_name='bundleassetprice',
            name='payment_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.PaymentType'),
        ),
        migrations.AddField(
            model_name='bank',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.City'),
        ),
        migrations.AddField(
            model_name='bank',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Country'),
        ),
        migrations.AddField(
            model_name='assetprice',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Currency'),
        ),
        migrations.AddField(
            model_name='assetprice',
            name='duration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.Duration'),
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together={('number', 'invoice_type', 'year')},
        ),
    ]
