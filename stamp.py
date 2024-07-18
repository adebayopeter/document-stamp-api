import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont


def split_text_to_fit(text, context, max_width, font_name="Helvetica", font_size=12, context_type='image'):
    words = text.split()
    lines = []
    current_line = ""

    if context_type == 'image':
        try:
            font = ImageFont.truetype("Helvetica.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
    else:
        font = font_name

    for word in words:
        test_line = current_line + " " + word if current_line else word
        if context_type == 'image':
            bbox = context.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        elif context_type == 'pdf':
            if context.stringWidth(test_line, font, font_size) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def stamp_pdf(file, stamp_text):
    # Read the uploaded PDF
    input_pdf = PdfReader(file)
    output_pdf = PdfWriter()

    # Create a stamped version of the document
    for page_number in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_number]

        # Get page dimensions
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        # Create a canvas to add the stamp
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))

        # Split the text into lines that fit within the page width
        lines = split_text_to_fit(stamp_text, can, width - 40)  # 40 to account for some margin

        # Calculate the initial y position to centralize the text vertically
        line_height = 12  # Assuming font size 12
        total_text_height = line_height * len(lines)
        y_position = (height - total_text_height) / 2

        # Draw each line of text
        for line in lines:
            text_width = can.stringWidth(line, 'Helvetica', 12)
            x_position = (width - text_width) / 2
            can.drawString(x_position, y_position, line)
            y_position -= line_height

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

    return send_file(output_stream, as_attachment=True,
                     download_name='stamped_document.pdf', mimetype='application/pdf')


def stamp_image(file, stamp_text):
    # Open the image file
    image = Image.open(file).convert("RGBA")
    width, height = image.size

    # Calculate font size (2.5% of image width)
    font_size = int(width * 0.025)  # 2.5% of image width

    # Create a blank RGBA image for the text overlay
    stamp = Image.new('RGBA', (width, height))

    # Create a drawing context
    draw = ImageDraw.Draw(stamp)

    # Define font (default PIL font)
    try:
        font_path = "font/helvetica/Helvetica.ttf"
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    # Split the text into lines that fit within the image width
    # 40 to account for some margin
    lines = split_text_to_fit(stamp_text, draw, width - 40, "Helvetica", font_size, context_type='image')

    # Calculate the total height of the text block
    mask = font.getmask(stamp_text)
    line_height = mask.size[1]
    total_text_height = line_height * len(lines)
    y_position = (height - total_text_height) // 2

    # Draw each line of text
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_position = (width - text_width) // 2
        draw.text((x_position, y_position), line, font=font, fill=(255, 255, 255, 255))  # White text
        y_position += line_height

    # Combine the original image with the text overlay
    stamped_image = Image.alpha_composite(image, stamp)

    output_stream = io.BytesIO()
    stamped_image.save(output_stream, format='PNG')
    output_stream.seek(0)

    return send_file(output_stream, as_attachment=True,
                     download_name='stamped_image.png', mimetype='image/png')


def stamp_pdf_with_image(file, stamp_image_file, signer_text=None):
    # Read the uploaded PDF
    input_pdf = PdfReader(file)
    output_pdf = PdfWriter()

    # Read the stamp image and add transparency
    stamp_img = Image.open(stamp_image_file).convert("RGBA")
    datas = stamp_img.getdata()

    new_data = []
    for item in datas:
        # Change all white (also shades of whites)
        # pixels to transparent
        if item[0] in list(range(200, 256)):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    stamp_img.putdata(new_data)

    # Save the modified image to a BytesIO object
    image_io = io.BytesIO()
    stamp_img.save(image_io, format='PNG')
    image_io.seek(0)
    transparent_stamp_image = ImageReader(image_io)

    # Create a stamped version of the document
    for page_number in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_number]

        # Create a canvas to add the stamp
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # check if signer_text is None
        if signer_text is not None:
            # Draw the text
            text = f"{signer_text}"
            # Adjust position as needed
            can.drawString(200, 650, text)

        # Adjust position and size as needed
        can.drawImage(transparent_stamp_image, 250, 550, width=100, height=100, mask='auto')
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

    return send_file(output_stream, as_attachment=True,
                     download_name='stamped_document.pdf', mimetype='application/pdf')


def stamp_image_with_image(file, stamp_image_file, signer_text=None):
    image = Image.open(file).convert("RGBA")
    stamp_img = Image.open(stamp_image_file).convert("RGBA")

    # Adjust the transparency of the stamp image
    datas = stamp_img.getdata()
    new_data = []
    for item in datas:
        if item[0] in list(range(200, 256)):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    stamp_img.putdata(new_data)

    # Adjust the size of the stamp image base on 20:100 ratio
    width, height = image.size
    stamp_ratio = 0.2

    # Calculate dimensions while maintaining the aspect ratio
    stamp_width = int(width * stamp_ratio)
    stamp_height = int(stamp_width * (stamp_img.height / stamp_img.width))

    # Resize the stamp image
    stamp_img = stamp_img.resize((stamp_width, stamp_height), Image.LANCZOS)

    # Create a new image with an alpha layer (RGBA)
    base = image.copy()

    # Paste the stamp image onto the base image
    base.paste(stamp_img, (width // 2 - stamp_width // 2, height // 2 - stamp_height // 2), stamp_img)

    # check if signer_text is None
    if signer_text is not None:
        # Create an overlay for the text
        txt_overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_overlay)

        # Draw the text on the overlay
        text_position = (width // 2 - stamp_width // 2, height // 2 - stamp_height // 2 - 20)
        draw.text(text_position, signer_text, fill=(0, 0, 0, 255))  # Adjust the text color as needed

        # Composite the text overlay onto the base image
        base = Image.alpha_composite(base, txt_overlay)

    output_stream = io.BytesIO()
    base.save(output_stream, format='PNG')
    output_stream.seek(0)

    return send_file(output_stream, as_attachment=True,
                     download_name='stamped_image.png', mimetype='image/png')

