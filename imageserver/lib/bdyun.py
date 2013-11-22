#!/usr/bin/env python
import hmac
import hashlib
import urllib
import base64
import requests
from datetime import datetime, timedelta


HOST = "http://bcs.duapp.com"


class BaiduYun(object):

    def __init__(self, ak, sk, bucket):
        self.ak = ak
        self.sk = sk
        self.bucket = bucket

    # Get the signature of the string 'content'
    def get_sign(self, content):
        hashed = hmac.new(self.sk, content, hashlib.sha1)
        sign = urllib.quote(base64.b64encode(hashed.digest()))
        return sign

    def get_content_sign(self, action, oname):
        flag = "MBO"
        content = flag + "\n"
        content += "Method=%s\n" % action
        content += "Bucket=%s\n" % self.bucket
        content += "Object=%s\n" % oname
        sign = self.get_sign(content)

        sign = "%s:%s:%s" % (flag, self.ak, sign)
        return sign

    #def get_object(self, self.bucket, oname):
    #    sign = self.get_content_sign("GET", self.bucket, oname)

    def put_object(self, oname, raw):
        sign = self.get_content_sign("PUT", oname)

        url = '{}/{}/{}?sign={}'.format(HOST.strip('/'), self.bucket.strip('/'), oname.strip('/'), sign)

        headers = {}
        headers['Content-Type'] = 'image/jpg'
        headers['Content-Length'] = str(len(raw))
        headers['x-bs-acl'] = 'public-read'
        expire = datetime.now() + timedelta(days=100000)
        headers['Expires'] = expire.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

        page = requests.put(url, data=raw, headers=headers)
        return page.status_code == 200


def test():
    AK = "PvjMabgn0qvG"
    SK = "kSplfWiOaDTi"
    bd = BaiduYun(AK, SK, 'yueduu')
    # test get object
    filename = "98548.2.jpg"
    with open(filename) as file:
        raw = file.read()
        bd.put_object("98548.2.jpg", raw)


if __name__ == '__main__':
    test()
