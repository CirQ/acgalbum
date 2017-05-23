import sys
import pickle
import urllib2
import imagehash
from io import BytesIO
from PIL import Image

def query(url):
    try:
        img_bytes = BytesIO(urllib2.urlopen(url).read())
        image = Image.open(img_bytes)
        fp = int(str(imagehash.phash(image)), 16)

        with open("fp.pkl", "r") as r:
            fps = map(lambda t:[t[0],int(t[1],16)], pickle.load(r))

        for afp in fps:
            afp[1] = bin(fp^afp[1]).count('1')
        return min(fps, key=lambda t:t[1])[0]
    except:
        return -1

print query(sys.argv[1])
