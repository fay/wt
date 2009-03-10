#coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36
class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    email = forms.EmailField(label=_(u'电子邮件'), error_message = _("This value must a valid email address"))
    password1 = forms.CharField(label=_(u"输入密码"), widget=forms.PasswordInput)
    #password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    username = forms.CharField(label=_(u"用户昵称"), max_length=30)

    class Meta:
        model = User
        fields = ("email","username",)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))
        
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_("A user with that email already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def get_username(self):
        return username
    def get_email(self):
        return email
    def __unicode__(self):
        return self._html_output(u'<tr><td>%(label)s%(errors)s%(field)s%(help_text)s</td></tr>', u'<tr><td colspan="2">%s</td></tr>', '</td></tr>', u'<br />%s', False)
    def as_table(self):
        return self._html_output(u'<tr><td>%(label)s%(errors)s%(field)s%(help_text)s</td></tr>', u'<tr><td colspan="2">%s</td></tr>', '</td></tr>', u'<br />%s', False)
