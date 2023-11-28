import os, ssl

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    RECAPTCHA_PUBLIC_KEY = '6LcY0BIpAAAAABFXtwRNnZgOUQZMzxpQ9Ir_yKr5'
    RECAPTCHA_PRIVATE_KEY = '6LcY0BIpAAAAAEKtb84yVfBEwGAvPES_mLSk4R-H'
    TESTING = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_SSL_VERSION = ssl.PROTOCOL_TLSv1_2
    ADMINS = os.environ.get('EMAIL_USER')