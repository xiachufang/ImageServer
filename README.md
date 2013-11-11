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
