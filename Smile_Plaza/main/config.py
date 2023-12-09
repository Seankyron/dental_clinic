import ssl

class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    RECAPTCHA_PUBLIC_KEY = '6LcY0BIpAAAAABFXtwRNnZgOUQZMzxpQ9Ir_yKr5'
    RECAPTCHA_PRIVATE_KEY = '6LcY0BIpAAAAAEKtb84yVfBEwGAvPES_mLSk4R-H'
    TESTING = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'brionessean500@gmail.com'
    MAIL_PASSWORD = 'avin eyvr ixoi oqwj'
    MAIL_SSL_VERSION = ssl.PROTOCOL_TLSv1_2
    ADMINS = 'brionessean500@gmail.com'