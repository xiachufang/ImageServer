#coding:utf-8
import Image
import ImageFile
from cStringIO import StringIO
from exceptions import IOError


class OpenImageException(Exception):
    pass


class ResizeImageException(Exception):
    pass


class ImageWrapper(object):
    def __init__(self, im_str=None, im=None):
        '''
            im_str: image string
            im: Image object
        '''
        self.im = im or picopen(im_str)
        self.im_str = im_str

    def __getattr__(self, k):
        return getattr(self.im, k)

    def to_string(self, quality=100):
        if quality == 100:
            return self.im_str or img2str(self.im, quality=95)

        return img2str(self.im, quality=quality)

    def resize_to(self, width, height=None):
        w = h = max_height = None

        w = int(width)
        if height.startswith('<'):
            max_height = int(height.lstrip('<'))
        else:
            h = int(height)

        return ImageWrapper(im=resize_to(self.im, w, h, max_height))


def picopen(image):
    if not image:
        raise OpenImageException('Image can not be empty')

    if hasattr(image, 'getim'): # a PIL Image object
        im = image
    else:
        if not hasattr(image, 'read'): # image content string
            image = StringIO(image)
        try:
            im = Image.open(image) # file-like object
        except IOError as e:
            raise OpenImageException(e)

    if im.mode == 'RGBA':
        p = Image.new('RGBA', im.size, 'white')
        try:
            x, y = im.size
            p.paste(im, (0, 0, x, y), im)
            im = p
        except Exception as e:
            raise OpenImageException(e)
        finally:
            del p

    if im.mode == 'P':
        need_rgb = True
    elif im.mode == 'L':
        need_rgb = True
    elif im.mode == 'CMYK':
        need_rgb = True
    else:
        need_rgb = False

    if need_rgb:
        im = im.convert('RGB', dither=Image.NONE)

    return im


def resize_to(im, width, height=None, max_height=None):
    im = picopen(im)
    if not width:
        raise ResizeImageException('Width can not be empty')

    if height:
        # 宽高都确定
        if width == height:
            return pic_square(im, width, height)

        return pic_fit(im, width, height)

    if max_height:
        # 定宽定最大高度
        # 等比例缩放到目标宽度后，如果高度大于需要的高度，则截取最上面的区域
        return pic_resize_width_cut_height_if_large(im, width, max_height)

    # 定宽不定高
    return pic_fix_width(im, width)


def pic_resize_width_cut_height_if_large(image, width, max_height=None):
    if not image:
        return
    if max_height is None:
        max_height = width * 2.5

    x, y = image.size
    if x != width:
        image = image.resize((width, (width*y)/x), Image.ANTIALIAS)

    if max_height:
        x, y = image.size
        if y > max_height:
            image = image.crop((0, 0, x, max_height))
    return image


def pic_fix_width(image, width, height=None):
    width0, height0 = image.size
    if (width0, height0) == (width, height):   # 大小正好，不用处理
        return image
    else:    ##按比例缩放到宽度为width
        r_height = height0 * width // width0
        image = image.resize((width, r_height), Image.ANTIALIAS)

    if not height:    ##不定高则直接返回缩放结果
        pass
    else:    ##定高则进行切图
        width_begin = 0
        height_begin = (r_height - height) // 2
        image = image.crop((width_begin, height_begin, width_begin+width, height_begin+height))

    return image


def pic_fit(image, width, height=None):
    if height is None:
        height = width

    x, y = image.size
    if x == width and y == height:
        return image

    #x*height > width*y 缩放到height,剪裁掉width
    x_h = x*height
    w_y = width*y

    if x_h != w_y:
        if x_h > w_y:
            cuted_height = height
            cuted_width = x*height//y
        else:
            cuted_height = y*width//x
            cuted_width = width
    else:
        cuted_width = width
        cuted_height = height
    image = image.resize((cuted_width, cuted_height), Image.ANTIALIAS)

    x, y = image.size

    # TODO: change 4 to 2 by subdragon
    if x_h != w_y:
        if x_h > w_y:
            width_begin = (x-width)//2
            height_begin = 0
        else:
            width_begin = 0
            height_begin = (y-height)//2

        image = image.crop((width_begin, height_begin, width_begin+width, height_begin+height))
    return image


def _calc_square(x, y, width, top_left, size, zoom_out):
    height_delta = width
    default = True # 是否使用默认缩放策略
    if top_left is not None:
        try:
            ax, ay = top_left
            if ax < 0 or ay < 0:
                default = True
            elif size <= 0:
                default = True
            elif ax + size > x:
                default = True
            elif ay + size > y:
                default = True
            else:
                # 用户指定了合法的参数，则使用用户指定缩放策略
                default = False
        except:
            pass

    resize = None
    if default:
        zoom_in = (x > width and y > width)
        background = (x < width or y < width)

        # 如果图过小，需要粘贴在一个白色背景的图片上
        px, py = (width-x)/2, (width-y)/2
        if px < 0:
            px = 0
        if py < 0:
            py = 0
        paste = (px, py)

        # 如果允许放大，就不再需要往白色背景图片上粘贴
        if zoom_out and background:
            zoom_out = x < y and 'x' or 'y'
            if zoom_out == 'x':
                nx = width
                ny = width*y/x
            else:
                nx = width*x/y
                ny = width
            resize = (nx, ny)

            x, y = resize
            ax, ay = (x-width)/2, (y-width)/2
            if ax < 0:
                ax = 0
            if ay < 0:
                ay = 0
            bx = ax + width
            by = ay + width
        else:
            # 计算如何缩小
            if x > width and y > width:
                if x > y:
                    ax, bx = (x-y)/2, (x+y)/2
                    ay, by = 0, y
                else:
                    ax, bx = 0, x
                    ay, by = (y-x)/2, (y+x)/2
                    height_delta = x
            else:
                ax, ay, bx, by = (x-width)/2, (y-width)/2, (x+width)/2, (y+width)/2
                if ax < 0:
                    bx += ax
                    ax = 0
                if ay < 0:
                    by += ay
                    ay = 0

        # 高 > 宽时，需要调整，上方、下方切掉的区域高度比例要是 1:3。
        if y > x and y > width:
            ay -= (y - height_delta) / 4
            by -= (y - height_delta) / 4
        if bx > x:
            bx = x
        if by > y:
            by = y
        crop = [ax, ay, bx, by]
    else:
        zoom_in = (size != width)
        crop = [ax, ay, ax + size, ay + size]
        background = False
        paste = (0, 0)
    return zoom_out, resize, crop, zoom_in, background, paste


def pic_square(im, width, top_left=None, size=0, zoom_out=True):
    x, y = im.size
    zoom_out, resize, crop, zoom_in, background, paste = \
        _calc_square(x, y, width, top_left, size, zoom_out)

    if zoom_out and resize:
        im = im.resize(resize, Image.ANTIALIAS)

    (ax, ay, bx, by) = crop
    if not ((ax, ay) == (0, 0) and (bx, by) == im.size):
        im = im.crop(crop)

    if not (zoom_out and resize):
        if zoom_in:
            try:
                im = im.resize((width, width), Image.ANTIALIAS)
            except:
                raise ResizeImageException()
        if background:
            p = Image.new('RGBA', (width, width), 'white')
            p.paste(im, paste)
            im = p
            del p

    return im


def img2str(image, quality=85, progressive=True):
    f = StringIO()
    image = image.convert('RGB')
    try:
        image.save(f, 'JPEG', quality=quality, optimize=True, progressive=progressive)
    except IOError:
        ImageFile.MAXBLOCK = image.size[0] * image.size[1]
        image.save(f, 'JPEG', quality=quality, optimize=True, progressive=progressive)
    return f.getvalue()
