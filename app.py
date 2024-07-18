from flask import Flask, request
from flasgger import Swagger, swag_from
from stamp import stamp_pdf, stamp_image, stamp_pdf_with_image, stamp_image_with_image

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/stamp/text', methods=['POST'])
@swag_from({
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


@app.route('/stamp/image', methods=['POST'])
@swag_from({
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
                }
            }
        }
    }
})
def stamp_document_image_only():
    file = request.files['file']
    stamp_image_file = request.files['stamp_image']

    file_ext = file.filename.split('.')[-1].lower()

    if file_ext in ['pdf']:
        return stamp_pdf_with_image(file, stamp_image_file)
    elif file_ext in ['png', 'jpg', 'jpeg']:
        return stamp_image_with_image(file, stamp_image_file)
    else:
        return "Unsupported file type", 400


@app.route('/stamp/image-transparent', methods=['POST'])
@swag_from({
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
def stamp_document_image_transparent():
    file = request.files['file']
    stamp_image_file = request.files['stamp_image']

    if file.content_type == 'application/pdf':
        return stamp_pdf_with_image(file, stamp_image_file)
    elif file.content_type.startswith('image/'):
        return stamp_image_with_image(file, stamp_image_file)
    else:
        return "Unsupported file type", 400


@app.route('/stamp/image-and-text', methods=['POST'])
@swag_from({
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
            'name': 'signer_name',
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
    file = request.files['file']
    stamp_image_file = request.files['stamp_image']
    signer_text = request.form.get('signer_text')

    if file.content_type == 'application/pdf':
        return stamp_pdf_with_image(file, stamp_image_file, signer_text)
    elif file.content_type.startswith('image/'):
        return stamp_image_with_image(file, stamp_image_file, signer_text)
    else:
        return "Unsupported file type", 400


if __name__ == '__main__':
    app.run(debug=True)
