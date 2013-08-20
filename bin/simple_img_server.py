from flask import Flask, make_response, abort
import pymongo
import gridfs

db = pymongo.MongoClient().rankomatic
fs = gridfs.GridFS(db)

app = Flask(__name__)
app.debug = True

@app.route('/<num>')
def serve_png_files(num):
    try:
        fname = 'SPo8Os8gxT/grammar%s.png' % num
        f = fs.get_last_version(filename=fname)
        response = make_response(f.read())
        response.mimetype = 'image/png'
        return response
    except gridfs.errors.NoFile:
        abort(404)

app.run()
