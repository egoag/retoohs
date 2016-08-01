from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from ss.models import SSUser, InviteCode, Node


class CrispyFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', '确定'))
        super(CrispyFormMixin, self).__init__(*args, **kwargs)


class SSUserForm(CrispyFormMixin, forms.ModelForm):
    invite_code = forms.CharField(max_length=40, min_length=24, label='邀请码')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(SSUserForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.user = self.user
        return super(SSUserForm, self).save(commit)

    class Meta:
        model = SSUser
        fields = ('password', 'invite_code')


class InviteCodeForm(CrispyFormMixin, forms.ModelForm):
    number = forms.IntegerField(label='数量', initial=1, required=False)
    code = forms.CharField(label='前缀', max_length=32, required=False)

    def __init__(self, *args, **kwargs):
        self.instances = []
        self.instance_number = 1
        super(InviteCodeForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(InviteCodeForm, self).clean()
        self.instance_number = cleaned_data.pop('number')
        return cleaned_data

    def save(self, commit=True):
        """
        Create many InviteCode instances
        :param commit:
        :return:
        """
        if self.errors:
            raise ValueError('data did not validate')
        code = self.cleaned_data.get('code')
        user = self.cleaned_data.get('user')
        for _ in range(self.instance_number):
            obj = self._meta.model.objects.create(code=code, user=user)
            self.instances.append(obj)
        self.instance = self.instances[0]
        return self.instance

    class Meta:
        model = InviteCode
        fields = ('user', 'code', 'number')
