import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
from flasgger import Swagger, swag_from
from stamp import stamp_pdf, stamp_image, stamp_pdf_with_image, stamp_image_with_image

# Load environment variables from .env file
load_dotenv()

# Determine the environment
base_url = os.getenv('BASE_URL', 'localhost:5000')

app = Flask(__name__)

# Custom Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

# Custom Swagger template with tags for grouping
template = {
    "swagger": "2.0",
    "info": {
        "title": "My Bucket API",
        "description": "API documentation to unlock the awesome and powerful possibilities with Python 🐍.",
        "version": "1.0.0"
    },
    "host": base_url,  # Change this to the appropriate host
    "basePath": "/",  # Base path for the endpoints
    "schemes": [
        "http",
        "https"
    ],
    "tags": [
        {
            "name": "Stamping",
            "description": "Operations related to stamping text/images/text & images on documents and images"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=template)


# Serve custom CSS and JavaScript
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/apidocs/')
def api_docs():
    return render_template('swagger_ui.html')


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
