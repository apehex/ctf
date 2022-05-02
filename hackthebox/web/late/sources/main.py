import datetime
import os, random
from flask.templating import render_template_string
from werkzeug.utils import secure_filename
import PIL.Image
import pytesseract
from PIL import Image
from flask import Flask, request, render_template, redirect, url_for, session, send_file

app = Flask(__name__)

upload_dir = "/home/svc_acc/app/uploads"
misc_dir = '/home/svc_acc/app/misc'
allowed_extensions =  ["jpg" ,'png']
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def home():
    return render_template("index.html", title="Image Reader")


@app.route('/scanner', methods=['GET', 'POST'])
def scan_file():
    scanned_text = ''
    results = ''
    if request.method == 'POST':
        start_time = datetime.datetime.now()
        f = request.files['file']
        
        if f.filename.split('.')[-1] in allowed_extensions:
            try:
                ID = str(random.randint(1,10000))
                file_name = upload_dir + "/" + secure_filename(f.filename )+ ID
                f.save(file_name)
                pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
                scanned_text = pytesseract.image_to_string(PIL.Image.open(file_name))

                results = """<p>{}</p>""".format(scanned_text)

                r = render_template_string(results)
                path = misc_dir + "/" + ID + '_' + 'results.txt'
            
                with open(path, 'w') as f:
                    f.write(r)

                return send_file(path, as_attachment=True,attachment_filename='results.txt')

            except Exception as e:
                return ('Error occured while processing the image: ' + str(e))
        else:
            return 'Invalid Extension'
