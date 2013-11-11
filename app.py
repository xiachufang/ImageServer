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
beans = Beansdb(BEANSDBCFG, 16)


@app.route('/upload', methods=['POST'])
def upload():
    '''size=100x50,200x200,300x0,150x<100'''
    size_str = request.form.get('sizes', '').strip()
    image = request.files.get('image')
    sizes = [xy.split('x') for xy in size_str.split(',') if xy]
    app.logger.debug('upload params sizes: %s', sizes)

    try:
        im = ImageWrapper(image)
    except OpenImageException:
        return error('Not a valid image!')

    ident = gen_ident()
    try:
        save_image_to_beansdb(im, ident, sizes)
    except WriteFailedError as e:
        return error('Save to beansdb error: %s' % e)
    return ok({'ident': ident, 'sizes': sizes})


@app.route('/image/<ident>.jpg')
def pic_show(ident):
    app.logger.debug('/image/%s', ident)
    width = request.args.get('width')
    height = request.args.get('height')
    ident_ = compute_ident(ident, width, height)
    app.logger.debug('get %s', ident_)
    image_binary = beans.get(ident_)
    if not image_binary:
        return error('Image corresponding to %s@%sx%s doesn\'t exist!' % (ident, width, height))
    return Response(image_binary, mimetype='image/jpeg')


@app.route('/image/<ident>.jpg', methods=['POST'])
def resize_image(ident):
    app.logger.debug('resize /image/%s', ident)
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
    app.logger.debug('set %s', ident)
    if sizes:
        resize_and_save_image_to_beansdb(im, ident, sizes)

    return ident


def resize_and_save_image_to_beansdb(im, ident, sizes=[]):
    for w, h in sizes:
        # save different sizes of images
        computed_ident = compute_ident(ident, w, h)
        temp_im = im.resize_to(w, h)
        beans.set(computed_ident, temp_im.to_string())
        app.logger.debug('set %s @%sx%s', computed_ident, w, h)
    return ident


def gen_ident():
    return uuid.uuid1().hex


def compute_ident(ident, width, height):
    if width and height:
        return '%s/%sx%s' % (ident, width, height)
    return ident


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
