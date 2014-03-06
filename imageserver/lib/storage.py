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

    def compute_ident(self, ident, width=None):
        if width:
            return '%s@%s' % (ident, width)
        return ident


class BeansStorage(BaseStorage):
    def __init__(self, conn, logger=None, quality=90):
        self.conn = conn
        self.logger = logger or Null
        self.quality = quality

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
        if not im:
            return
        self.set(ident, im.to_string(quality=95))
        self.logger.debug('Beans set %s', ident)
        if sizes:
            self._resize_image(ident, ImageWrapper(im=im), sizes)

        return ident

    def get_image(self, ident, width=None):
        ident_ = self.compute_ident(ident, width)
        self.logger.debug('Beans get %s', ident_)
        return ImageWrapper(self.get(ident_))

    def resize_image(self, ident, sizes=[]):
        im = self.get_image(ident)
        if not im:
            return []
        return self._resize_image(ident, im, sizes)

    def _resize_image(self, ident, im, sizes=[]):
        return list(self._lazy_resize_image(ident, im, sizes))

    def _lazy_resize_image(self, ident, im, sizes=[]):
        for w, h in sizes:
            # save different sizes of images
            computed_ident = self.compute_ident(ident, w)
            temp_im = im.resize_to(w, h)
            temp_im_str = temp_im.to_string(quality=self.quality)
            self.set(computed_ident, temp_im_str)
            self.logger.debug('Beans set %s @%sx%s', computed_ident, w, h)
            yield temp_im_str
