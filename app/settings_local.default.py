DEBUG = True
SECRET_KEY = '4ohxt@6bv11x4*$7knh62d498u%-f@78)t_)7z(tzo_!#j+t!0'
ALLOWED_HOSTS = ['127.0.0.1']

STATIC_ROOT = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
