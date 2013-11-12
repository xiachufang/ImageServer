import uuid
from flask import Flask, request, jsonify, Response
from dbclient import Beansdb, WriteFailedError
from image import ImageWrapper, OpenImageException


app = Flask(__name__)

BEANSDBCFG = {
    "localhost:7901": range(16),
    "localhost:7902": range(16),
}
HOST = ''
HEIGHT_IN_IDENT = False
beans = Beansdb(BEANSDBCFG, 16)


@app.route('/upload', methods=['POST'])
def upload():
    '''size=100x50,200x200,300x0,150x<100'''
    size_str = request.form.get('sizes', '').strip()
    image = request.files.get('image')
    sizes = [xy.split('x') for xy in size_str.split(',') if xy]
    ident = request.form.get('ident', '').strip()

    try:
        im = ImageWrapper(image)
    except OpenImageException:
        return error('Not a valid image!')

    if ident:
        # Data contained in the key might be huge, so get the corresponing meta data.
        if beans.get('?%s' % ident):
            # if uploading to a specified ident, check wheather the ident has data in it first.
            return error('Can not replace existing data')
    else:
        # generate an unique ident
        ident = gen_ident()

    try:
        save_image_to_beansdb(im, ident, sizes)
    except WriteFailedError as e:
        return error('Save to beansdb error: %s' % e)
    return ok({'ident': ident, 'sizes': sizes})


@app.route('/image/<width>/<height>/<ident>.jpg')
def pic_show(width, height, ident):
    ident_ = compute_ident(ident, width, height)
    if not ident_:
        return error('Image corresponding to %s@%sx%s doesn\'t exist!' % (ident, width, height))
    app.logger.debug('Beans get: %s', ident_)
    image_binary = beans.get(ident_)
    if not image_binary:
        return error('Image corresponding to %s@%sx%s doesn\'t exist!' % (ident, width, height))
    return Response(image_binary, mimetype='image/jpeg')


@app.route('/image/<width>/<ident>.jpg')
def pic_show3(width, ident):
    return pic_show(width, None, ident)


@app.route('/image/<ident>.jpg')
def pic_shows(ident):
    '''width and height are in query parameters'''
    width = request.args.get('width')
    height = request.args.get('height')
    return pic_show(width, height, ident)


@app.route('/image/<ident>.jpg', methods=['POST'])
def resize_image(ident):
    size_str = request.form.get('sizes', '').strip()
    sizes = [xy.split('x') for xy in size_str.split(',') if xy]
    image_binary = beans.get(ident)
    if not image_binary:
        return error('Image corresponding to %s does\'n exist!' % ident)

    try:
        im = ImageWrapper(image_binary)
        resize_and_save_image_to_beansdb(im, ident, sizes)
    except (WriteFailedError, OpenImageException) as e:
        return error(e)
    return ok({'ident': ident, 'sizes': sizes})


def save_image_to_beansdb(im, ident, sizes=[]):
    '''
    im: ImageWrapper object
    ident: identity
    sizes: 100x50,200x200,300x0,150x<100
    '''
    # save the original image
    beans.set(ident, im.to_string())
    app.logger.debug('Beans set %s', ident)
    if sizes:
        resize_and_save_image_to_beansdb(im, ident, sizes)

    return ident


def resize_and_save_image_to_beansdb(im, ident, sizes=[]):
    for w, h in sizes:
        # save different sizes of images
        computed_ident = compute_ident(ident, w, h)
        temp_im = im.resize_to(w, h)
        beans.set(computed_ident, temp_im.to_string())
        app.logger.debug('Beans set %s @%sx%s', computed_ident, w, h)
    return ident


def gen_ident():
    return uuid.uuid1().hex


def compute_ident(ident, width=None, height=None):
    if not height and not width:
        # ident for original image
        return ident

    if HEIGHT_IN_IDENT:
        if height and width:
            return '%s@%sx%s' % (ident, width, height)
        return ''

    if width:
        return '%s@%s' % (ident, width)
    return ''


def get_pic_url(ident):
    return '%s/image/%s.jpg' % (HOST, ident)


def ok(res):
    return jsonify({
        'status': 'ok',
        'content': res,
    })


def error(res):
    return jsonify({
        'status': 'error',
        'content': res,
    })


if __name__ == "__main__":
    app.run(use_debugger=True, use_reloader=True, debug=True, host='0.0.0.0', port=33370)
