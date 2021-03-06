# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from phonenumber_field.modelfields import PhoneNumberField

from main.declarations import USER_TYPES
from hacktrick.tasks import send_email_for_information
from .utils import validate_avatar_dimensions


@python_2_unicode_compatible
class Profile(AbstractUser):
    user_type = models.SmallIntegerField('user tipi', choices=USER_TYPES, default=3)
    email = models.EmailField('email address', unique=True)
    institution = models.CharField('kurum/üniversite', blank=True, max_length=100)
    phone_number = PhoneNumberField('telefon', blank=True, help_text='format: +905306602321')


    def save(self, *args, **kwargs):
        if self.pk is None:
            extra = "<br/> İsim: {}".format(self.get_full_name())
            extra = "<br/>"
            extra += "Kullanıcı adı: {}".format(self.username)
            send_email_for_information.delay(email_type=0, email_to=[self.email], extra=extra)
        else:
            prev = Profile.objects.get(pk=self.pk)
            if prev.user_type != self.user_type and self.user_type == 2:
                send_email_for_information.delay(email_type=5, email_to=[self.email], extra="")

        super(Profile, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.username


class Instructor(models.Model):
    user = models.OneToOneField(
        Profile,
        verbose_name='Kullanıcı',
        related_name='instructor',
        related_query_name='instructor'
    )
    title = models.CharField('Başlık', max_length=100)
    institution = models.CharField('Kurum', max_length=100)
    image = models.ImageField(
        upload_to='instructor/',
        verbose_name='Resim',
        blank=True,
        null=True,
        validators=[validate_avatar_dimensions]
    )
    facebook = models.CharField(help_text='facebook kullanıcı adı', max_length=50, blank=True)
    twitter = models.CharField(help_text='twitter kullanıcı adı', max_length=50, blank=True)
    linkedin = models.CharField(help_text='linkedin kullanıcı adı', max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Eğitmenler"
        verbose_name = "Eğitmen"

    def __str__(self):
        return self.user.username

    def clean(self, *args, **kwargs):
        if not self.user.user_type == 2:
            raise ValidationError('Seçtiğiniz kullanıcının tipi eğitmen olmak zorundadır.')
        super(Instructor, self).clean(*args, **kwargs)
