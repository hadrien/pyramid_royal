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

    @staticmethod
    def replace_author(db, old_author, new_author):
        spec = {'author': old_author}
        update = {'$set': {'author': new_author}}
        db.Photo.find_and_modify(spec, update)
