from flask import Flask, request, jsonify, render_template, url_for
from flasgger import Swagger, swag_from
from stamp import stamp_pdf, stamp_image, stamp_pdf_with_image, stamp_image_with_image

app = Flask(__name__)

# Basic Swagger template with tags for grouping
template = {
    "tags": [
        {
            "name": "Stamping",
            "description": "Operations related to stamping text/images/text & images on documents and images"
        }
    ]
}

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "My API Documentation",
        "description": "API documentation for my bucket stamping application.",
        "version": "0.0.1"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ]
})


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/apidocs/')
def api_docs():
    return "API Documentation"


@app.route('/api/stamp/text', methods=['POST'])
@swag_from({
    'tags': ['Stamping'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'PDF or image file to be stamped'
        },
        {
            'name': 'stamp',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Text to be used as stamp'
        }
    ],
    'responses': {
        200: {
            'description': 'Stamped file',
            'content': {
                'application/pdf': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                },
                'image/png': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                },
                'image/jpeg': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        }
    }
})
def stamp_document_text_only():
    file = request.files['file']
    stamp_text = request.form.get('stamp', 'CONFIDENTIAL')

    file_ext = file.filename.split('.')[-1].lower()

    if file_ext in ['pdf']:
        return stamp_pdf(file, stamp_text)
    elif file_ext in ['png', 'jpg', 'jpeg']:
        return stamp_image(file, stamp_text)
    else:
        return "Unsupported file type", 400


@app.route('/api/stamp/image', methods=['POST'])
@swag_from({
    'tags': ['Stamping'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'PDF or image file to be stamped'
        },
        {
            'name': 'stamp_image',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Image file to be used as stamp'
        }
    ],
    'responses': {
        200: {
            'description': 'Stamped file',
            'content': {
                'application/pdf': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                },
                'image/png': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                },
                'image/jpeg': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        }
    }
})
def stamp_document_image():
    file = request.files['file']
    stamp_image_file = request.files['stamp_image']

    file_ext = file.filename.split('.')[-1].lower()

    if file_ext in ['pdf']:
        return stamp_pdf_with_image(file, stamp_image_file)
    elif file_ext in ['png', 'jpg', 'jpeg']:
        return stamp_image_with_image(file, stamp_image_file)
    else:
        return "Unsupported file type", 400


@app.route('/api/stamp/image-and-text', methods=['POST'])
@swag_from({
    'tags': ['Stamping'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'PDF or image file to be stamped'
        },
        {
            'name': 'stamp_image',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Image file to be used as stamp'
        },
        {
            'name': 'signer_text_message',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Signer name to be included in the stamp'
        }
    ],
    'responses': {
        200: {
            'description': 'Stamped PDF file',
            'content': {
                'application/pdf': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                },
                'image/png': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                },
                'image/jpeg': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        }
    }
})
def stamp_document_image_text():
    # json_request = request.json
    file = request.files['file']
    stamp_image_file = request.files['stamp_image']
    signer_text = request.form.get('signer_text_message')

    file_ext = file.filename.split('.')[-1].lower()

    if file_ext in ['pdf']:
        return stamp_pdf_with_image(file, stamp_image_file, signer_text)
    elif file_ext in ['png', 'jpg', 'jpeg']:
        return stamp_image_with_image(file, stamp_image_file, signer_text)
    else:
        return "Unsupported file type", 400


if __name__ == '__main__':
    app.run(debug=True)
