from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Field, Row, Column
from crispy_forms.bootstrap import PrependedText, InlineCheckboxes, InlineRadios

class SystemsDropdownForm(forms.Form):
	def __init__(self, *args, **kwargs):
		systems = kwargs.pop('systems',0)
		super(SystemsDropdownForm, self).__init__(*args, **kwargs)

		systemChoices = [('','Select a system')]
		for system in systems:
			systemId = system['id']
			systemChoices.append((systemId,systemId))

		self.fields['systems'] = forms.ChoiceField(label='', choices=systemChoices, required=False)
		self.helper = FormHelper(self)

class SystemsGrantRole(forms.Form):
	updateUser = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Username'}))
	roleChoices = [('GUEST', 'Guest'), ('USER','User'), ('PUBLISHER','Publisher')]
	role = forms.ChoiceField(label='', choices=roleChoices, initial='GUEST')
	def __init__(self, *args, **kwargs):
		super(SystemsGrantRole, self).__init__(*args, **kwargs)
		
		self.helper = FormHelper(self)
		self.helper.layout = Layout('updateUser',InlineRadios('role'))
		self.helper[0].wrap(Column, css_class='col-md-3')
		self.helper[1].wrap(Column, css_class='col-md-4')
		self.helper[0:2].wrap_together(Row, css_class='form_row')

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

class AppsGrantPermission(forms.Form):
	updateUser = forms.CharField(label='',
								 widget=forms.TextInput(attrs={'placeholder': 'Username'}))
	permChoices = [('r','Read'), ('w','Write'), ('x','Execute')]
	perm = forms.MultipleChoiceField(label='', choices=permChoices)
	def __init__(self, *args, **kwargs):
		super(AppsGrantPermission, self).__init__(*args, **kwargs)

		self.helper = FormHelper(self)
		self.helper.layout = Layout('updateUser',InlineCheckboxes('perm'))
		self.helper[0].wrap(Column, css_class='col-md-3')
		self.helper[1].wrap(Column, css_class='col-md-4')
		self.helper[0:2].wrap_together(Row, css_class='form_row')
