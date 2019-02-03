from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Field, Row, Column
from crispy_forms.bootstrap import PrependedText
class JobSubmitForm(forms.Form):
	name = forms.CharField(label='Job Name')
	email = forms.EmailField(help_text='Email to receive notifications')

	def __init__(self, *args, **kwargs):
		parameters = kwargs.pop('parameters', 0)
		systems = kwargs.pop('availableSystems',0)
		super(JobSubmitForm, self).__init__(*args, **kwargs)

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

		# Parameter Fields
		for parameter in parameters:
			label 			= parameter['details']['label']
			description 	= parameter['details']['description']
			required 		= parameter['value']['required']
			parameterType 	= parameter['value']['type']
			parameterId 	= parameter['id']
			if parameterType == 'number':
				self.fields['sweepPara_{parameterId}_start'.format(parameterId=parameterId)] = forms.IntegerField(label= '', required=required, help_text=description)
				self.fields['sweepPara_{parameterId}_end'.format(parameterId=parameterId)] = forms.IntegerField(label='', required=required)
				self.fields['sweepPara_{parameterId}_num'.format(parameterId=parameterId)] = forms.IntegerField(label='', required=required)
			elif parameterType == 'string':
				self.fields['para_{parameterId}'.format(parameterId=parameterId)] = forms.CharField(label=label, required=required, help_text=description)
			elif parameterType == 'bool':
				self.fields['para_{parameterId}'.format(parameterId=parameterId)] = forms.BooleanField(label=label, required=required, help_text=description)
			elif parameterType == 'flag':
				self.fields['para_{parameterId}'.format(parameterId=parameterId)] = forms.BooleanField(label=label, required=required, help_text=description)
			elif parameterType == 'enumeration':
				enum_values = parameter['value']['enum_values']
				choices = {}
				for choice in enum_values:
					choices.update(choice)
				choices = [ (k,v) for k, v in choices.items() ]
				self.fields['para_{parameterId}'.format(parameterId=parameterId)] = forms.ChoiceField(label=label, required=required, help_text=description, choices=choices)
			else:
				print('Unexpected parameter type: %s' % parameterType)

		# Create Form Layout
		self.helper = FormHelper(self)
		self.helper.layout = Layout(
			'name','email','storageSystem','executionSystem'
		)
		self.helper[0:4].wrap(Column, css_class='col-md-6')
		self.helper[2:4].wrap_together(Row, css_class='form_row')
		self.helper[0:2].wrap_together(Row, css_class='form_row')

		for parameter in parameters:
			parameterType 	= parameter['value']['type']
			parameterId 	= parameter['id']
			if parameterType == 'number':
				label = parameter['details']['label']
				self.helper.layout.append(Field(PrependedText('sweepPara_{parameterId}_start'.format(parameterId=parameterId), 'Start')))
				self.helper.layout.append(Field(PrependedText('sweepPara_{parameterId}_end'.format(parameterId=parameterId), 'End')))
				self.helper.layout.append(Field(PrependedText('sweepPara_{parameterId}_num'.format(parameterId=parameterId), 'Number')))
				self.helper[len(self.helper)-3:].wrap(Column, css_class='col-md-4')
				self.helper[len(self.helper)-3:].wrap_together(Row, css_class='form_row')
				self.helper[len(self.helper)-1].wrap_together(Fieldset, label)
			else:
				self.helper.layout.append('para_{parameterId}'.format(parameterId=parameterId))

		self.helper.layout.append(Submit('submit', 'Submit'))