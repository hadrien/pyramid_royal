import logging
import shutil

from example.model import base

log = logging.getLogger(__name__)


class Photo(base.Document):
    __collection__ = 'photos'

    structure = {
        u'author': unicode,
        }

    gridfs = {'files': ['image']}

    required = structure.keys()

    indexes = [
        {'fields': u'author'},
        ]

    @staticmethod
    def create(db, author, image_file, image_mime_type):
        photo = db.Photo()
        photo.author = author
        photo.save()
        with photo.fs.new_file('image') as fp:
            try:
                fp.content_type = image_mime_type
                shutil.copyfileobj(image_file, fp)
            except Exception:
                log.exception('Image file copy on db=%s, photo_id=%s', db,
                              photo._id)
                raise
        return photo

    def update(db, label, title, description, payload, image, image_mime_type):
        achievement = db.Achievement.one({'label': label})
        if achievement is None:
            achievement = db.Achievement()
        achievement.label = label
        achievement.title = title
        achievement.description = description
        achievement.payload = payload
        achievement.save()
        with achievement.fs.new_file('image') as fp:
            try:
                fp.content_type = image_mime_type
                shutil.copyfileobj(image, fp)
            except:
                log.exception('Achievement image file copy on db=%s', db)
                raise
        return achievement
