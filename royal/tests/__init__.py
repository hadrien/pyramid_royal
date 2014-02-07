import os


def setupPackage():
    os.environ['MONGO_URI'] = 'mongodb://localhost'
    os.environ['MONGO_DB_NAME'] = 'royal_example'
    os.environ['MONGO_DB_PREFIX'] = ''
