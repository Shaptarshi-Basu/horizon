# Copyright 2013 Centrin Data Systems Ltd.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django import shortcuts
from django.conf import settings
from django.contrib.auth import authenticate # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

import horizon
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import functions as utils
from openstack_dashboard import api
from openstack_auth import exceptions as auth_exceptions


class EmailForm(forms.SelfHandlingForm):
    email = forms.EmailField(
            label=_("Email"),
            required=True)
    password = forms.CharField(label=_("Current password"),
                           widget=forms.PasswordInput(render_value=False))

    # We have to protect the entire "data" dict because it contains the
    # password string.
    @sensitive_variables('data')
    def handle(self, request, data):
        #the user's password to change the email, only to update the password
        user_is_editable = api.keystone.keystone_can_edit_user()
        if user_is_editable:
            try:
                #check if the password is correct
                password = data['password']
                domain = getattr(settings,
                                'OPENSTACK_KEYSTONE_DEFAULT_DOMAIN',
                                'Default')
                default_region = (settings.OPENSTACK_KEYSTONE_URL, "Default Region")
                region = getattr(settings, 'AVAILABLE_REGIONS', [default_region])[0][0]
                #import pdb; pdb.set_trace()
                username = request.user.username
                result = authenticate(request=request,
                                                username=username,
                                                password=password,
                                                user_domain_name=domain,
                                                auth_url=region)
                #now update email
                user_id=request.user.id
                user = api.keystone.user_get(request,user_id,admin=False)
                
                api.keystone.user_update(request,user,email=data['email'],
                                        password=None)#if we dont set password to None we get a dict-key error in api/keystone
                msg = _("Email changed succesfully")
                messages.success(request,msg)
                
                response = shortcuts.redirect(horizon.get_user_home(request.user))
                return response
            except auth_exceptions.KeystoneAuthException as exc:
                messages.error(request,_('Invalid password'))
                return False

            except Exception:
                exceptions.handle(request,
                                  _('Unable to change email.'))
                return False
        else:
            messages.error(request, _('Changing email is not supported.'))
            return False