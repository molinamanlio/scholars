from django.conf import settings
from django.db import models

from gdstorage.storage import GoogleDriveStorage
from model_utils import Choices

from users.models import User
from utils.models import TimeStampable


gd_storage = GoogleDriveStorage()


class Course(TimeStampable):
    STATUS = Choices(
        (0, 'draft', 'Draft'),
        (1, 'in_progress', 'In Progress'),
        (2, 'published', 'Published')
    )

    gid = models.CharField(max_length=256, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=512, unique=True)
    owner = models.ForeignKey(User, related_name='courses')
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.draft)

    def __unicode__(self):
        return "%s (%d slides)" % (self.name, self.slides.count())

    def __str__(self):
        return "%s (%d slides)" % (self.name, self.slides.count())


def get_image_path(instance, filename):
    import os
    full_name = os.path.join(
        "%d" % instance.course.id, "images", "%03d.png" % instance.position)
    media_path = os.path.join(settings.MEDIA_ROOT, full_name)
    if os.path.exists(media_path):
        os.remove(media_path)
    return full_name


def get_audio_path(instance, filename):
    import os
    full_name = os.path.join(
        "%d" % instance.course.id, "audio", "%03d.mp3" % instance.position)
    media_path = os.path.join(settings.MEDIA_ROOT, full_name)
    if os.path.exists(media_path):
        os.remove(media_path)
    return full_name


class Slide(TimeStampable):
    STATUS = Choices(
        (0, 'draft', 'Draft'),
        (1, 'in_progress', 'In Progress'),
        (2, 'pending_approval', 'Pending Approval'),
        (3, 'published', 'Published')
    )

    gid = models.CharField(max_length=256, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    audio = models.FileField(upload_to=get_audio_path, null=True, blank=True)
    notes = models.TextField(max_length=5000, null=True, blank=True)
    position = models.PositiveIntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='slides')
    status = models.PositiveIntegerField(choices=STATUS, default=STATUS.draft)
    assigned_to = models.ForeignKey(User, related_name='slides', null=True, blank=True)

    class Meta:
        # unique_together = ('course', 'position')
        ordering = ['position']

    def image_url(self):
        return u'<img src="%s" style="max-width:250px;max-height:250px" />' % self.image.url

    image_url.short_description = 'Image'
    image_url.allow_tags = True

    def audio_url(self):
        return u'<audio controls src="%s" style="max-width:200px;" />' % self.audio.url

    audio_url.short_description = 'Audio'
    audio_url.allow_tags = True


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from utils.utils import export
# @receiver(post_save, sender=Course)
# def update_slides(sender, instance=None, created=False, **kwargs):
#     if instance.id is not None and instance.gid is not None:
#         export(instance.id, instance.gid)