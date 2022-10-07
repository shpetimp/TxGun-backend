from ..model_base import NicknamedBase
from django.db import models

class ErrorLog(NicknamedBase):
    traceback = models.TextField()
    transaction = models.TextField(null=True, blank=True)
    level = models.CharField(max_length=16, default='exception')

    @classmethod
    def WARNING(cls, name, details, **kwargs):
        return cls.objects.create(nickname=name,
            traceback=details,
            level='warning',
            **kwargs)
