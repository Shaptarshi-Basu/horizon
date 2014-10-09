from django import shortcuts
from django.conf import settings
from django import forms 
from django.utils.translation import ugettext_lazy as _

import horizon
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import functions as utils
from openstack_dashboard import api
from openstack_auth import exceptions as auth_exceptions


class CreateApplicationForm(forms.SelfHandlingForm):
	name = forms.CharField(label=_("Name"), required=False)
	description = forms.CharField(label=_("Description"),widget=forms.Textarea, required=False)
	url = forms.CharField(label=_("URL"), required=False)
	callbackurl = forms.CharField(label=_("Callback URL"), required=False)

	def handle(self, request, data):
		response = shortcuts.redirect(update)
		return response
	
	
class UploadImageForm(forms.Form):
	file = forms.ImageField(required=False)

	def handle(self, request, data):
		response = shortcuts.redirect('roles')
		return response
	

class RolesApplicationForm(forms.SelfHandlingForm):
	name = forms.CharField(label=_("Name"), required=False)
	# roles = forms.ChoiceField( 'Provider', 'Purchaser')

	def handle(self, request, data):
		user_id=request.user.id
		user = api.keystone.user_get(request,user_id,admin=False)
		response = shortcuts.redirect(horizon.get_user_home(request.user))
		return response
	