#coding: utf8
import uuid
from .null import Null
from .image import ImageWrapper


class BaseStorage(object):
    def set(self, key, value):
        pass

    def get(self, key):
        pass

    def gen_ident(self):
        return uuid.uuid1().hex

    def compute_ident(self, ident, width=None, height=None):
        if not height and not width:
            # ident for original image
            return ident

        if self.height_in_ident:
            if height and width:
                return '%s@%sx%s' % (ident, width, height)
            return ''

        if width:
            return '%s@%s' % (ident, width)
        return ''


class BeansStorage(BaseStorage):
    def __init__(self, conn, height_in_ident=False, logger=None):
        self.conn = conn
        self.height_in_ident = height_in_ident
        self.logger = logger or Null

    def set(self, key, value):
        return self.conn.set(key, value)

    def get(self, key):
        return self.conn.get(key)

    def set_image(self, ident, im, sizes=[]):
        '''
        ident: identity
        im: ImageWrapper object
        sizes: 100x50,200x200,300x0,150x<100
        '''
        # save the original image
        self.set(ident, im.to_string())
        self.logger.debug('Beans set %s', ident)
        if sizes:
            self._resize_image(ident, im, sizes)

        return ident

    def get_image(self, ident, width=None, height=None):
        ident_ = self.compute_ident(ident, width, height)
        self.logger.debug('Beans get %s', ident_)
        return ImageWrapper(self.get(ident_))

    def resize_image(self, ident, sizes=[]):
        im = self.get(ident)
        return self._resize_image(ident, im, sizes)

    def _resize_image(self, ident, im, sizes=[]):
        for w, h in sizes:
            # save different sizes of images
            computed_ident = self.compute_ident(ident, w, h)
            temp_im = im.resize_to(w, h)
            self.set(computed_ident, temp_im.to_string(quality=90))
            self.logger.debug('Beans set %s @%sx%s', computed_ident, w, h)
        return ident
