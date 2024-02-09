from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from sorl.thumbnail import ImageField
from sorl.thumbnail import delete
import uuid
import os
import datetime
from django.core.files import File as FileOs

from PIL import Image
import urllib.request


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    now = datetime.datetime.now()

    directory = "%s/%s/%s" % (now.year, now.month, now.day)
    return os.path.join(directory, filename)


class File(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    file = models.FileField(null=True, blank=True, upload_to=get_file_path)
    name = models.CharField(max_length=250, blank=True)
    type = models.CharField(max_length=200, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def _get_file_url(self):
        if self.file:
            return self.file.url
        else:
            return None

    file_url = property(_get_file_url)

    def save(self, *args, **kwargs):
        params = {
            'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
            'CacheControl': 'max-age=94608000',
            'ContentDisposition': 'attachments; filename="%s"' % self.name}

        self.file.storage.object_parameters = params

        return super(File, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


def delete_file_on_file_delete(sender, instance, **kwargs):
    if (instance.file):
        instance.file.delete(save=False)


post_delete.connect(delete_file_on_file_delete, sender=File)


class UserImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, related_name='user_images', on_delete=models.SET_NULL)
    file = ImageField(null=True, blank=True, upload_to=get_file_path)
    name = models.CharField(max_length=250, blank=True)
    type = models.CharField(max_length=200, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def _get_file_url(self):
        if self.file:
            return self.file.url
        else:
            return None

    file_url = property(_get_file_url)

    def __unicode__(self):
        return self.name


class UrlImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.URLField(blank=True, null=True, unique=True, db_index=True)
    file = ImageField(null=True, blank=True, upload_to=get_file_path)
    create_date = models.DateTimeField(auto_now_add=True)

    def _get_file_url(self):
        if self.file:
            return self.file.url
        else:
            return None

    file_url = property(_get_file_url)

    def __unicode__(self):
        return self.url


def get_external_image_url(site_url, url):
    try:
        url_file = UrlImage.objects.get(url=site_url)
        return url_file.file_url
    except UrlImage.DoesNotExist:

        opener = urllib.request.build_opener()
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0')]
        urllib.request.install_opener(opener)
        if url.find('//') == 0:
            url = url.replace('//', 'http://')

        try:
            result = urllib.request.urlretrieve(url)
        except:
            return None
        try:
            img = Image.open(result[0])
            img.verify()
        except:
            return None

        try:
            url_file = UrlImage.objects.create(url=site_url)
            new_file = FileOs(open(result[0], 'rb'))
            url_file.file.save(os.path.basename(img.format),
                               new_file
                               )
            url_file.save()
            return url_file.file_url

        except:
            return None


def delete_image_on_image_delete(sender, instance, **kwargs):
    if (instance.file):
        delete(instance.file)


post_delete.connect(delete_image_on_image_delete, sender=UserImage)
