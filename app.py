import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
from flasgger import Swagger, swag_from
from stamp import stamp_pdf, stamp_image, stamp_pdf_with_image, stamp_image_with_image

# Load environment variables from .env file
load_dotenv()

# Determine the environment
base_url = os.getenv('BASE_URL', 'localhost:5000')

app = Flask(__name__)

# Ensure the 'downloads' directory exists
if not os.path.exists('downloads'):
    os.makedirs('downloads')


# Configure logging
logging.basicConfig(filename='stamping.log', level=logging.INFO, format='%(asctime)s - %(message)s')


def log_stamp_activity(file_name):
    logging.info(f'File stamped: {file_name}')


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
    'consumes': [
        'multipart/form-data',
        'application/json'
    ],
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
        },
        {
            'name': 'position',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Position to affix the stamp (top, center, bottom, right, left)'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'PDF or image file to be stamped'
                    },
                    'stamp': {
                        'type': 'string',
                        'description': 'Text to be used as stamp'
                    },
                    'position': {
                        'type': 'string',
                        'description': 'Position to affix the stamp (top, center, bottom, right, left)'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Stamped file',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {
                                'type': 'string'
                            },
                            'download_link': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }
    }
})
def stamp_document_text_only():
    if request.is_json:
        data = request.get_json()
        file = data.get('file')
        stamp_text = data.get('stamp', 'CONFIDENTIAL')
        position = data.get('position', 'center')
    else:
        file = request.files['file']
        stamp_text = request.form.get('stamp', 'CONFIDENTIAL')
        position = request.form.get('position', 'center')

    file_ext = file.filename.split('.')[-1].lower()

    if file_ext in ['pdf']:
        output_path = stamp_pdf(file, stamp_text, position)
        log_stamp_activity(output_path)
        return jsonify({
            'status': 'success',
            'download_link': url_for('download_file', filename=output_path, _external=True)
        })
    elif file_ext in ['png', 'jpg', 'jpeg']:
        output_path = stamp_image(file, stamp_text, position)
        log_stamp_activity(output_path)
        return jsonify({
            'status': 'success',
            'download_link': url_for('download_file', filename=output_path, _external=True)
        })
    else:
        return jsonify({'status': 'fail', 'message': 'Unsupported file type'}), 400


@app.route('/api/stamp/image', methods=['POST'])
@swag_from({
    'tags': ['Stamping'],
    'consumes': [
        'multipart/form-data',
        'application/json'
    ],
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
            'name': 'position',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Position to affix the stamp (top, center, bottom, right, left)'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'PDF or image file to be stamped'
                    },
                    'stamp_image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Image file to be used as stamp'
                    },
                    'position': {
                        'type': 'string',
                        'description': 'Position to affix the stamp (top, center, bottom, right, left)'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Stamped file',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {
                                'type': 'string'
                            },
                            'download_link': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }
    }
})
def stamp_document_image():
    if request.is_json:
        data = request.get_json()
        file = data.get('file')
        stamp_image_file = data.get('stamp_image')
        position = data.get('position', 'center')
    else:
        file = request.files['file']
        stamp_image_file = request.files['stamp_image']
        position = request.form.get('position', 'center')

    file_ext = file.filename.split('.')[-1].lower()

    if file_ext in ['pdf']:
        output_path = stamp_pdf_with_image(file, stamp_image_file, position)
        log_stamp_activity(output_path)
        return jsonify({
            'status': 'success',
            'download_link': url_for('download_file', filename=output_path, _external=True)
        })
    elif file_ext in ['png', 'jpg', 'jpeg']:
        output_path = stamp_image_with_image(file, stamp_image_file, position)
        log_stamp_activity(output_path)
        return jsonify({
            'status': 'success',
            'download_link': url_for('download_file', filename=output_path, _external=True)
        })
    else:
        return jsonify({'status': 'fail', 'message': 'Unsupported file type'}), 400


@app.route('/api/stamp/image-and-text', methods=['POST'])
@swag_from({
    'tags': ['Stamping'],
    'consumes': [
        'multipart/form-data',
        'application/json'
    ],
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
        },
        {
            'name': 'position',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Position to affix the stamp (top, center, bottom, right, left)'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'PDF or image file to be stamped'
                    },
                    'stamp_image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Image to be used as stamp'
                    },
                    'signer_text_message': {
                        'type': 'string',
                        'description': 'Signer name to be included in the stamp'
                    },
                    'position': {
                        'type': 'string',
                        'description': 'Position to affix the stamp (top, center, bottom, right, left)'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Stamped file',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {
                                'type': 'string'
                            },
                            'download_link': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }
    }
})
def stamp_document_image_text():
    if request.is_json:
        data = request.get_json()
        file = data.get('file')
        stamp_image_file = data.get('stamp_image')
        signer_text = data.get('signer_text_message')
        position = data.get('position', 'center')
    else:
        file = request.files['file']
        stamp_image_file = request.files['stamp_image']
        signer_text = request.form.get('signer_text_message')
        position = request.form.get('position', 'center')

    file_ext = file.filename.split('.')[-1].lower()

    if file_ext in ['pdf']:
        output_path = stamp_pdf_with_image(file, stamp_image_file, signer_text, position)
        log_stamp_activity(output_path)
        return jsonify({
            'status': 'success',
            'download_link': url_for('download_file', filename=output_path, _external=True)
        })
    elif file_ext in ['png', 'jpg', 'jpeg']:
        output_path = stamp_image_with_image(file, stamp_image_file, signer_text, position)
        log_stamp_activity(output_path)
        return jsonify({
            'status': 'success',
            'download_link': url_for('download_file', filename=output_path, _external=True)
        })
    else:
        return jsonify({'status': 'fail', 'message': 'Unsupported file type'}), 400


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('downloads', filename)


if __name__ == '__main__':
    app.run(debug=True)
