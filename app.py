from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from flasgger import Swagger, swag_from
import io
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/stamp', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'PDF file to be stamped'
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
            'description': 'Stamped PDF file',
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
def stamp_document():
    file = request.files['file']
    stamp_text = request.form.get('stamp', 'CONFIDENTIAL')

    # Read the uploaded PDF
    input_pdf = PdfReader(file)
    output_pdf = PdfWriter()

    # Create a stamped version of the document
    for page_number in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_number]

        # Create a canvas to add the stamp
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(100, 500, stamp_text)
        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)

        # Read the canvas as a PDF
        new_pdf = PdfReader(packet)

        # Merge the canvas PDF with the existing page
        page.merge_page(new_pdf.pages[0])
        output_pdf.add_page(page)

    # Save the result
    output_stream = io.BytesIO()
    output_pdf.write(output_stream)
    output_stream.seek(0)

    return send_file(output_stream, as_attachment=True, download_name='stamped_document.pdf')


@app.route('/stamp_image', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'PDF file to be stamped'
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
            'description': 'Stamped PDF file',
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
def stamp_document_image():
    file = request.files['file']
    stamp_image_file = request.files['stamp_image']

    # Read the uploaded PDF
    input_pdf = PdfReader(file)
    output_pdf = PdfWriter()

    # Read the stamp image
    stamp_image = ImageReader(stamp_image_file)

    # Create a stamped version of the document
    for page_number in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_number]

        # Create a canvas to add the stamp
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawImage(stamp_image, 300, 500, width=100, height=100)  # Adjust position and size as needed
        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)

        # Read the canvas as a PDF
        new_pdf = PdfReader(packet)

        # Merge the canvas PDF with the existing page
        page.merge_page(new_pdf.pages[0])
        output_pdf.add_page(page)

    # Save the result
    output_stream = io.BytesIO()
    output_pdf.write(output_stream)
    output_stream.seek(0)

    return send_file(output_stream, as_attachment=True, download_name='stamped_document.pdf')


@app.route('/stamp_image_transparent', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'PDF file to be stamped'
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
            'description': 'Stamped PDF file',
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
def stamp_document_image_transparent():
    file = request.files['file']
    stamp_image_file = request.files['stamp_image']

    # Read the uploaded PDF
    input_pdf = PdfReader(file)
    output_pdf = PdfWriter()

    # Read the stamp image and add transparency
    stamp_image = Image.open(stamp_image_file).convert("RGBA")
    datas = stamp_image.getdata()

    new_data = []
    for item in datas:
        # Change all white (also shades of whites)
        # pixels to transparent
        if item[0] in list(range(200, 256)):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    stamp_image.putdata(new_data)

    # Save the modified image to a BytesIO object
    image_io = io.BytesIO()
    stamp_image.save(image_io, format='PNG')
    image_io.seek(0)
    transparent_stamp_image = ImageReader(image_io)

    # Create a stamped version of the document
    for page_number in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_number]

        # Create a canvas to add the stamp
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawImage(transparent_stamp_image, 250, 550, width=100, height=100, mask='auto')  # Adjust position and size as needed
        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)

        # Read the canvas as a PDF
        new_pdf = PdfReader(packet)

        # Merge the canvas PDF with the existing page
        page.merge_page(new_pdf.pages[0])
        output_pdf.add_page(page)

    # Save the result
    output_stream = io.BytesIO()
    output_pdf.write(output_stream)
    output_stream.seek(0)

    return send_file(output_stream, as_attachment=True, download_name='stamped_document.pdf')


@app.route('/stamp_image_text', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'PDF file to be stamped'
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
                }
            }
        }
    }
})
def stamp_document_image_text():
    file = request.files['file']
    stamp_image_file = request.files['stamp_image']
    signer_name = request.form.get('signer_name', 'Adebayo')

    # Read the uploaded PDF
    input_pdf = PdfReader(file)
    output_pdf = PdfWriter()

    # Read the stamp image and add transparency
    stamp_image = Image.open(stamp_image_file).convert("RGBA")
    datas = stamp_image.getdata()

    new_data = []
    for item in datas:
        # Change all white (also shades of whites)
        # pixels to transparent
        if item[0] in list(range(200, 256)):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    stamp_image.putdata(new_data)

    # Save the modified image to a BytesIO object
    image_io = io.BytesIO()
    stamp_image.save(image_io, format='PNG')
    image_io.seek(0)
    transparent_stamp_image = ImageReader(image_io)

    # Create a stamped version of the document
    for page_number in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_number]

        # Create a canvas to add the stamp
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Draw the text
        text = f"This document was signed by {signer_name}"
        can.drawString(200, 650, text)  # Adjust position as needed

        # Draw the stamp image
        can.drawImage(transparent_stamp_image, 250, 550, width=100, height=100, mask='auto')  # Adjust position and size as needed
        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)

        # Read the canvas as a PDF
        new_pdf = PdfReader(packet)

        # Merge the canvas PDF with the existing page
        page.merge_page(new_pdf.pages[0])
        output_pdf.add_page(page)

    # Save the result
    output_stream = io.BytesIO()
    output_pdf.write(output_stream)
    output_stream.seek(0)

    return send_file(output_stream, as_attachment=True, download_name='stamped_document.pdf')


if __name__ == '__main__':
    app.run(debug=True)
