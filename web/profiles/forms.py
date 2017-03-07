# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.forms.widgets import TextInput, Textarea

from nocaptcha_recaptcha.fields import NoReCaptchaField

from .models import Profile, Instructor
from hacktrick.models import Ticket, TicketComment


class UserProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['institution', 'phone_number']

        widgets = {
            'institution': TextInput(attrs={'placeHolder': 'Kurum/Üniversite'}),
            'phone_number': TextInput(attrs={'placeHolder': 'Telelfon numarası(+90 000 000 00 00)'}),
        }
        labels = {
            'institution': 'Kurum/Üniversite',
            'phone': 'Telefon'
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['institution'].required = True
        self.fields['phone_number'].required = True


class InstructorForm(ModelForm):
    class Meta:
        model = Instructor
        fields = ['title', 'institution', 'image', 'facebook', 'twitter', 'linkedin']

        widgets = {
            'institution': TextInput(attrs={'placeHolder': 'Kurum/Üniversite'}),
            'title': TextInput(attrs={'placeHolder': 'Ünvan'}),
            'facebook': TextInput(attrs={'placeHolder': 'Facebook kullanıcı adı'}),
            'twitter': TextInput(attrs={'placeHolder': 'Twitter kullanıcı adı'}),
            'linkedin': TextInput(attrs={'placeHolder': 'Linkedin kullanıcı adı'}),
        }


class TicketForm(ModelForm):
    captcha = NoReCaptchaField()

    class Meta:
        model = Ticket
        fields = ['title', 'content']

        widgets = {
            'title': TextInput(attrs={'placeHolder': 'Başlık'}),
            'content': Textarea(attrs={'placeHolder': 'İçerik', 'style': 'width:100% !important;'}),
        }

    def save(self, user=None, commit=True):
        instance = super(TicketForm, self).save(commit=False)
        instance.user = user
        if commit:
            instance.save()
            # TODO: Send email to admin
        return instance

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(TicketForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(TicketForm, self).clean()
        if Ticket.objects.filter(user=self.request.user).count() >= 5:
            raise ValidationError("Bir kullanıcı 5'den fazla soru soramaz.")
        return cleaned_data


class TicketCommentForm(ModelForm):
    captcha = NoReCaptchaField()

    class Meta:
        model = TicketComment
        fields = ['comment']

        widgets = {
            'comment': Textarea(attrs={'placeHolder': 'Yorum yap', 'style': 'width:100% !important;'}),
        }

    def __init__(self, *args, **kwargs):
        self.ticket = kwargs.pop('ticket')
        super(TicketCommentForm, self).__init__(*args, **kwargs)

    def save(self, user=None, ticket=None, commit=True):
        instance = super(TicketCommentForm, self).save(commit=False)
        instance.user = user
        instance.ticket = ticket
        if commit:
            instance.save()
            # TODO: Send email to admin and user
        return instance

    def clean(self):
        cleaned_data = super(TicketCommentForm, self).clean()
        comment_count =  TicketComment.objects.filter(ticket=self.ticket).count()
        if comment_count == 0:
            raise ValidationError("Cevap verilmeyen bir soruya yorum yapamazsınız. "
                                  "Lütfen moderatörün cevap vermesini bekleyin.")
        elif comment_count >= 5:
            raise ValidationError("Bir soruya 5'dan fazla yorum eklenemez.")
        return cleaned_data
