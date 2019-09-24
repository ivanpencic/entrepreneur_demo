from django.contrib import admin
import billing.models as models
import billing.operations as operations
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from django.forms import ModelForm, PasswordInput

app = apps.get_app_config('billing')


class PersonalDataAdmin(admin.ModelAdmin):
	fields = ('first_name_enc', 'last_name_enc', 'address_enc')
	# exclude = ('first_name_enc', 'last_name_enc', 'address_enc')
admin.site.register(models.PersonalData, PersonalDataAdmin)


class EmailForm(ModelForm):
	class Meta:
		model = models.Email
		fields = ('personal_data', 'email_enc', 'email_password_enc',)
		widgets = {
			'email_password_enc': PasswordInput(),
		}

	def __init__(self, *args, **kwargs):
		if kwargs.get('instance', None):
			if not kwargs.get('initial'):
				kwargs['initial'] = {}
			kwargs['initial'].update({
				'email_enc': operations.decrypt_value(
					kwargs['instance'].personal_data.salt,
					kwargs['instance'].email_enc
				),
			})
		super(EmailForm, self).__init__(*args, **kwargs)


class EmailFormAdmin(admin.ModelAdmin):
	form = EmailForm
	# import pdb;pdb.set_trace()
admin.site.register(models.Email, EmailFormAdmin)


for model_name, model in app.models.items():
	try:
		admin.site.register(model)
	except AlreadyRegistered:
		pass
