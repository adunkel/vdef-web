from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Field, Row, Column
from crispy_forms.bootstrap import PrependedText

class AppsDropdownForm(forms.Form):
	def __init__(self, *args, **kwargs):
		apps = kwargs.pop('apps',0)
		super(AppsDropdownForm, self).__init__(*args, **kwargs)

		appChoices = [('','Select an application')]
		for app in apps:
			appId = app['id']
			appChoices.append((appId,appId))

		self.fields['apps'] = forms.ChoiceField(label='', choices=appChoices, required=False)
		self.helper = FormHelper(self)
		self.helper.layout = Layout('apps')