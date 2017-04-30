from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model, authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Button, Row, Field
from avatar import forms as avatar_forms


class CrispyFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', '确定'))
        super(CrispyFormMixin, self).__init__(*args, **kwargs)


class RegisterForm(auth_forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', '确定', css_class="btn-primary", style="margin-left:18px; width: 98px"))
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')


class LoginForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(label='密码', strip=False, widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': "用户名/密码错误.",
        'inactive': "账户已停用.",
    }

    def __init__(self, request=None, redirect_to=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        if 'course_id' in kwargs:
            self.course_id = kwargs.pop('course_id')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', '确定', css_class="btn-primary", style="margin-left:18px; width: 98px"))
        self.helper.add_input(Button('forgot-password', '找回密码', css_class="btn-warning",
                                     style="margin-left:18px; width: 98px", onclick="location.href='/password_reset';"))
        super(LoginForm, self).__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None
        # Set the label for the "username" field.
        user_model = get_user_model()
        self.username_field = user_model._meta.get_field(user_model.USERNAME_FIELD)
        if redirect_to:
            self.fields['next'] = forms.CharField(initial=redirect_to, widget=forms.HiddenInput)
        if self.fields['username'].label is None:
            self.fields['username'].label = self.username_field.verbose_name

            # self.helper.add_input(
            #     Button('button', '找回密码', onclick='window.location.href="/password-reset"',
            #            style="margin-left:18px; width: 98px"))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class PasswordChangeForm(CrispyFormMixin, auth_forms.PasswordChangeForm):
    pass


class PasswordResetForm(CrispyFormMixin, auth_forms.PasswordResetForm):
    def get_users(self, email):
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return active_users


class SetPasswordForm(CrispyFormMixin, auth_forms.SetPasswordForm):
    pass


class UploadAvatarForm(CrispyFormMixin, avatar_forms.UploadAvatarForm):
    pass


class DeleteAvatarForm(CrispyFormMixin, avatar_forms.DeleteAvatarForm):
    pass
