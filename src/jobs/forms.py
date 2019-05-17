from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Field, Row, Column
from crispy_forms.bootstrap import PrependedText, InlineCheckboxes, InlineRadios

class JobSearchForm(forms.Form):
	jobName = forms.CharField(label='Job Name')

	def __init__(self, *args, **kwargs):
		super(JobSearchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.layout = Layout('jobName')
		self.helper.layout.append(Submit('submit', 'Submit'))

class JobSetupForm(forms.Form):

	def __init__(self, *args, **kwargs):
		inputs = kwargs.pop('inputs', 0)
		systems = kwargs.pop('availableSystems',0)
		super(JobSetupForm, self).__init__(*args, **kwargs)

		# System Fields
		storageChoices = []
		executionChoices = []
		for system in systems:
			systemId = system['id']
			if system['type'] == 'EXECUTION':
				executionChoices.append((systemId,systemId))
			elif system['type'] == 'STORAGE':
				storageChoices.append((systemId,systemId))
			else:
				print('Unexpected system type')
		self.fields['storageSystem'] = forms.ChoiceField(label='Archive System', choices=storageChoices)
		self.fields['executionSystem'] = forms.ChoiceField(label='Execution System', choices=executionChoices)

		# File Input Fields
		for file in inputs:
			label 		= file['details']['label']
			description = file['details']['description']
			required 	= file['value']['required']
			inputId 	= file['id']
			self.fields[inputId] = forms.FileField(label=label, required=required, help_text=description)

		# Create Form Layout
		self.helper = FormHelper(self)
		self.helper.layout = Layout('storageSystem','executionSystem')
		self.helper[0:2].wrap(Column, css_class='col-md-6')
		self.helper[0:2].wrap_together(Row, css_class='form_row')

		for file in inputs:
			inputId 	= file['id']
			self.helper.layout.append(inputId)

		self.helper.layout.append(Submit('submit', 'Continue'))

class JobSubmitForm(forms.Form):
	name = forms.CharField(label='Job Name')
	email = forms.EmailField(help_text='Email to receive notifications',required=False)

	samplingChoices = [('grid', 'Grid'), ('random','Random'), ('latinSqaure','Latin Square')]
	sampling = forms.ChoiceField(label='Sampling Strategy', choices=samplingChoices, initial='grid')

	def __init__(self, *args, **kwargs):
		parameters = kwargs.pop('parameters', 0)
		super(JobSubmitForm, self).__init__(*args, **kwargs)

		# Parameter Fields
		for parameter in parameters:
			self.fields['sweepPara_{parameter}_start'.format(parameter=parameter)] = forms.FloatField(label= '', required=True)
			self.fields['sweepPara_{parameter}_end'.format(parameter=parameter)] = forms.FloatField(label='', required=True)
			self.fields['sweepPara_{parameter}_num'.format(parameter=parameter)] = forms.IntegerField(label='', required=True)

		# Create Form Layout
		self.helper = FormHelper(self)
		self.helper.layout = Layout(
			'name','email'
		)
		self.helper[0:2].wrap(Column, css_class='col-md-6')
		self.helper[0:2].wrap_together(Row, css_class='form_row')

		for parameter in parameters:
			self.helper.layout.append(Field(PrependedText('sweepPara_{parameter}_start'.format(parameter=parameter), 'Start')))
			self.helper.layout.append(Field(PrependedText('sweepPara_{parameter}_end'.format(parameter=parameter), 'End')))
			self.helper.layout.append(Field(PrependedText('sweepPara_{parameter}_num'.format(parameter=parameter), 'Number')))
			self.helper[len(self.helper)-3:].wrap(Column, css_class='col-md-4')
			self.helper[len(self.helper)-3:].wrap_together(Row, css_class='form_row')
			self.helper[len(self.helper)-1].wrap_together(Fieldset, parameter)

		self.helper.layout.append(InlineRadios('sampling'))
		self.helper.layout.append(Submit('submit', 'Submit'))