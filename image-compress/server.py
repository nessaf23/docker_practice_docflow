from flask import Flask, request, send_file
from PIL import Image
import io
import tempfile
import os

app = Flask(__name__)

COMPRESS_RATIO = int(os.environ.get('COMPRESS_RATIO', 5))
IMAGE_PATH = os.environ.get('IMAGE_PATH', '/tmp')
PORT=18080

@app.route('/compress', methods=['POST'])
def compress_image():
    if 'image' not in request.files:
        return {'error': 'No image provided'}, 400
    
    image_file = request.files['image']
    try:
        img = Image.open(image_file.stream)
    except:
        return {'error': 'Invalid image file'}, 400

    ratio = COMPRESS_RATIO
    if ratio <= 0:
        return {'error': 'Invalid server configuration'}, 500

    # Calculate new dimensions
    width, height = img.size
    new_width = int(width / ratio)
    new_height = int(height / ratio)

    # Resize image
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)

    # Prepare response
    imgfile = tempfile.NamedTemporaryFile(mode='w+t',
                                          dir=IMAGE_PATH,
                                          suffix=f".{img.format}",
                                          prefix='compressed_',
                                          delete=False)
    image_file.close()
    resized_img.save(imgfile.name, format=img.format)

    # returns message with tempfile name
    return {'message': imgfile.name.split('/')[-1]}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
