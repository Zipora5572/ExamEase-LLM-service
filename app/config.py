import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
   

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
