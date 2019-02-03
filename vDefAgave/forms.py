from django import forms

class JobSubmitForm(forms.Form):
	name = forms.CharField(label='Job Name')
	email = forms.EmailField(help_text='Email to receive notifications')

	def __init__(self, *args, **kwargs):
		parameters = kwargs.pop('parameters', 0)
		systems = kwargs.pop('availableSystems',0)
		print(systems)
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
				self.fields['para_{parameterId}'.format(parameterId=parameterId)] = forms.IntegerField(label=label, required=required, help_text=description)
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
				print(choices)
				self.fields['para_{parameterId}'.format(parameterId=parameterId)] = forms.ChoiceField(label=label, required=required, help_text=description, choices=choices)
			else:
				print('Unexpected parameter type: %s' % parameterType)