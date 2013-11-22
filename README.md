ImageServer
===========
Dependencies
-----------
ImageServer depends on `flask`, `celery`, `redis`, `PIL` and `Beansdb`. You should make sure those components avaliable before using ImageServer.


Run
-------
1. You need to setup Beansdb before use ImageServer.

        beansdb -p 7901 -d -P/tmp/beansdb1.pid -L/tmp/beansdb1.log -H /home/gfreezy/beans/db/db1 -vv
        beansdb -p 7902 -d -P/tmp/beansdb2.pid -L/tmp/beansdb2.log -H /home/gfreezy/beans/db/db2 -vv

2. Customize settings.

    Rename `sample_config.py` to `config.py`.

2. Run Server

    Run the following commands in the directory of ImageServer.

        $ python -m simpleserver.app

    If you want ImageServer to auto synchronise your images to BaiduYun, start celery first. Run the command in a new shell.

        $ celery worker -A simpleserver.init


API
--------
* `POST /upload` Upload image

        Form:
          image: Image string
          sizes(optional): 100x50,150x<60

          widthxheight or widthx<height

        Response:
        {
            "content": {
                "ident": "1c449b644ab111e3937900163e200a0a",
                "sizes": [
                    ["100", "50"],
                    ["150", "<60"]
                ]
            },
            "status": "ok"
        }

* `GET /image/<ident>.jpg` Visit image

        /image/1c449b644ab111e3937900163e200a0a.jpg?width=50&height=0
        /image/1c449b644ab111e3937900163e200a0a.jpg?width=50&height=<50
        /image/1c449b644ab111e3937900163e200a0a.jpg

* `POST /image/<ident>.jpg` Resize image

        Form:
          sizes(optional): 100x50,150x<60

          widthxheight or widthx<height

        Response:
        {
            "content": {
                "ident": "1c449b644ab111e3937900163e200a0a",
                "sizes": [
                    ["100", "50"],
                    ["150", "<60"]
                ]
            },
            "status": "ok"
        }
