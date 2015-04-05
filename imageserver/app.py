from flask import request, jsonify, Response
from .lib.dbclient import WriteFailedError
from .lib.image import ImageWrapper, OpenImageException
from .init import app, beans
from .tasks import async_upload_to_cloud


@app.after_request
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,OPTIONS,PUT,POST'
    return resp


@app.route('/upload', methods=['POST'])
def upload():
    '''size=100x50,200x200,300x0,150x<100'''
    size_str = request.form.get('sizes', '').strip()
    image = request.files.get('image')
    sizes = [xy.split('x') for xy in size_str.split(',') if xy]
    ident = request.form.get('ident', '').strip()
    callback = request.form.get('callback', '').strip()
    sync = request.form.get('sync', 'true').strip()

    app.logger.debug('callback %s', callback)
    try:
        im = ImageWrapper(image)
    except OpenImageException as e:
        return error(str(e))

    if ident:
        # Data contained in the key might be huge, so get the corresponing meta data.
        if beans.get('?%s' % ident):
            # if uploading to a specified ident, check wheather the ident has data in it first.
            return error('Can not replace existing data')
    else:
        # generate an unique ident
        ident = beans.gen_ident()

    try:
        beans.set_image(ident, im, sizes)
    except WriteFailedError as e:
        return error('Save to beansdb error: %s' % e)

    app.logger.debug('sync: %s', sync)
    if sync == 'true':
        async_upload_to_cloud.delay(ident, sizes, callback=callback)

    return ok({'ident': ident, 'sizes': sizes})


@app.route('/image/<ident>.jpg', methods=['POST'])
@app.route('/resize/<ident>.jpg', methods=['POST'])
def resize_image(ident):
    size_str = request.form.get('sizes', '').strip()
    sizes = [xy.split('x') for xy in size_str.split(',') if xy]
    callback = request.form.get('callback', '').strip()
    sync = request.form.get('sync', 'true').strip()

    app.logger.debug('callback %s', callback)
    try:
        beans.resize_image(ident, sizes)
    except (WriteFailedError, OpenImageException) as e:
        return error('Resize image error: %r' % e)

    if sync == 'true':
        async_upload_to_cloud.delay(ident, sizes, callback=callback)

    return ok({'ident': ident, 'sizes': sizes})


@app.route('/sync/<ident>.jpg', methods=['POST'])
def sync_image(ident):
    size_str = request.form.get('sizes', '').strip()
    sizes = [xy.split('x') for xy in size_str.split(',') if xy]
    callback = request.form.get('callback', '').strip()

    app.logger.debug('callback %s', callback)
    async_upload_to_cloud.delay(ident, sizes, callback=callback)

    return ok({'ident': ident, 'sizes': sizes})


@app.route('/image/<width>/<height>/<ident>.jpg')
def pic_show(width, height, ident):
    ident_ = beans.compute_ident(ident, width, height)
    if not ident_:
        return error('Image corresponding to %s@%sx%s doesn\'t exist!' % (ident, width, height), status_code=404)
    app.logger.debug('Beans get: %s', ident_)
    image_binary = beans.get(ident_)
    if not image_binary:
        return error('Image corresponding to %s@%sx%s doesn\'t exist!' % (ident, width, height), status_code=404)
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


def ok(res):
    return jsonify({
        'status': 'ok',
        'content': res,
    })


def error(res, status_code=400):
    return jsonify({
        'status': 'error',
        'content': res,
    }), status_code
