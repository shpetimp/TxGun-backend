from tritium.conf import *
IS_TEST=True

print('TEST MODE DEFAULTS, disabling unneeded plugins')
import logging
logging.disable(logging.CRITICAL)
DEBUG = True
print('TEST MODE: DEBUG=%s'%DEBUG)

# Once we reach a certain degree of complexity, this needs to be removed
print('TEST MODE: Using sqlite DB')
DATABASES['default']={
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': '.sqlite-test-db',
}
print('TEST MODE: Use fast MD5PasswordHasher')
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

from django.core.mail.backends.base import BaseEmailBackend
from django.core import mail
print('TEST MODE: Using dummy MockEmailBackend')
class MockEmailBackend(BaseEmailBackend):
    def send_messages(self, messages):
        if(hasattr(mail, 'outbox')):
            mail.outbox.extend(messages)
        return len(messages)

EMAIL_BACKEND='conf.test_settings.MockEmailBackend'
