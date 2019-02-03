from django import forms

class JobSubmitForm(forms.Form):
	name = forms.CharField()
	email = forms.EmailField()

	def __init__(self, *args, **kwargs):
		parameters = kwargs.pop('parameters', 0)

		super(JobSubmitForm, self).__init__(*args, **kwargs)
		for parameter in parameters:
			label = parameter['details']['label']
			description = parameter['details']['description']
			required = parameter['value']['required']
			parameterType = parameter['value']['type']
			parameterId = parameter['id']
			if parameterType == 'number':
				self.fields['{parameterId}'.format(parameterId=parameterId)] = forms.IntegerField(label=label, required=required, help_text=description)
			elif parameterType == 'string':
				self.fields['{parameterId}'.format(parameterId=parameterId)] = forms.CharField(label=label, required=required, help_text=description)
			elif parameterType == 'bool':
				self.fields['{parameterId}'.format(parameterId=parameterId)] = forms.BooleanField(label=label, required=required, help_text=description)
			elif parameterType == 'flag':
				self.fields['{parameterId}'.format(parameterId=parameterId)] = forms.BooleanField(label=label, required=required, help_text=description)
			elif parameterType == 'enumeration':
				enum_values = parameter['value']['enum_values']
				choices = {}
				for choice in enum_values:
					choices.update(choice)
				choices = [ (k,v) for k, v in choices.items() ]
				self.fields['{parameterId}'.format(parameterId=parameterId)] = forms.ChoiceField(label=label, required=required, help_text=description, choices=choices)
			else:
				print('Unexpected parameter type: %s' % parameterType)