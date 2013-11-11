ImageServer
===========

API
--------
* `POST /upload` Upload image

        Form:
          image: Image string
          sizes(optional): 100x50,150x<60
            widthxheight or widthx<height

* `GET /image/<ident>.jpg` Visit image

        /image/1c449b644ab111e3937900163e200a0a.jpg?width=50&height=0
        /image/1c449b644ab111e3937900163e200a0a.jpg?width=50&height=<50
        /image/1c449b644ab111e3937900163e200a0a.jpg

* `POST /image/<ident>.jpg` Resize image

      Form:
        sizes(optional): 100x50,150x<60
          widthxheight or widthx<height

Setup
-------
1. You need to setup Beansdb before use the service.

        beansdb -p 7901 -d -P/tmp/beansdb1.pid -L/tmp/beansdb1.log -H /home/gfreezy/beans/db/db1 -vv
        beansdb -p 7902 -d -P/tmp/beansdb2.pid -L/tmp/beansdb2.log -H /home/gfreezy/beans/db/db2 -vv

2. Run Server

        python app.py

