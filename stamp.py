import io
import os
import uuid
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from flask import send_file
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


def calculate_position(width, height, stamp_width, stamp_height, position):
    if position == 'top':
        return (width - stamp_width) // 2, height - stamp_height - 10
    elif position == 'bottom':
        return (width - stamp_width) // 2, 10
    elif position == 'left':
        return 10, (height - stamp_height) // 2
    elif position == 'right':
        return width - stamp_width - 10, (height - stamp_height) // 2
    else:
        # center
        return (width - stamp_width) // 2, (height - stamp_height) // 2


def generate_unique_filename(extension):
    unique_id = uuid.uuid4()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{unique_id}_{timestamp}.{extension}"


# stamp pdf with text
def stamp_pdf(file, stamp_text, position='center'):
    # Read the uploaded PDF
    input_pdf = PdfReader(file)
    output_pdf = PdfWriter()

    output_filename = generate_unique_filename('pdf')
    output_path = os.path.join('downloads', output_filename)

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
        # 40 to account for some margin
        lines = split_text_to_fit(stamp_text, can, width - 40, 'Helvetica', 12, context_type='pdf')

        # Draw each line of text
        for line in lines:
            text_width = can.stringWidth(line, 'Helvetica', 12)
            x_position, y_position = calculate_position(width, height, text_width, 12, position)
            can.drawString(x_position, y_position, line)

        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)

        # Read the canvas as a PDF
        new_pdf = PdfReader(packet)

        # Merge the canvas PDF with the existing page
        page.merge_page(new_pdf.pages[0])
        output_pdf.add_page(page)

    with open(output_path, 'wb') as output_file:
        output_pdf.write(output_file)

    return output_filename


# stamp image with text
def stamp_image(file, stamp_text, position='center'):
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

    # Draw each line of text
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_position, y_position = calculate_position(width, height, text_width, font_size, position)
        draw.text((x_position, y_position), line, font=font, fill=(255, 255, 255, 255))  # White text

    # Combine the original image with the text overlay
    stamped_image = Image.alpha_composite(image, stamp)

    extension = file.filename.split('.')[-1].lower()
    output_filename = generate_unique_filename(extension)
    output_path = os.path.join('downloads', output_filename)

    stamped_image.save(output_path, format=extension)

    return output_filename


# stamp pdf with image or/and text
def stamp_pdf_with_image(file, stamp_image_file, signer_text=None, position='center'):
    # Read the uploaded PDF
    input_pdf = PdfReader(file)
    output_pdf = PdfWriter()

    output_filename = generate_unique_filename('pdf')
    output_path = os.path.join('downloads', output_filename)

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

        # Get page dimensions
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        # Create a canvas to add the stamp
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))

        # check if signer_text is None
        if signer_text is not None:
            # Split the text into lines that fit within the page width
            lines = split_text_to_fit(signer_text, can, width - 40, 'Helvetica', 12, context_type='pdf')

            # Calculate the total height of the text block
            line_height = 12
            total_text_height = line_height * len(lines)
            y_position = 0

            # Draw each line of text
            for line in lines:
                text_width = can.stringWidth(line, 'Helvetica', 12)
                x_position, y_position = calculate_position(width, height, text_width, 12, position)
                can.drawString(x_position, y_position, line)

            y_position -= total_text_height

        else:
            y_position = height / 2  # Center the image vertically if no text

        # Adjust position and size as needed
        stamp_width = 100
        stamp_height = 100
        x_stamp,  y_stamp = calculate_position(width, height, stamp_width, stamp_height, position)
        can.drawImage(transparent_stamp_image, x_stamp, y_stamp,
                      width=stamp_width, height=stamp_height, mask='auto')
        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)

        # Read the canvas as a PDF
        new_pdf = PdfReader(packet)

        # Merge the canvas PDF with the existing page
        page.merge_page(new_pdf.pages[0])
        output_pdf.add_page(page)

    with open(output_path, 'wb') as output_file:
        output_pdf.write(output_file)

    return output_filename


def stamp_image_with_image(file, stamp_image_file, signer_text=None, position='center'):
    image = Image.open(file).convert("RGBA")
    stamp_img = Image.open(stamp_image_file).convert("RGBA")

    # Adjust the transparency of the stamp image
    new_data = [(255, 255, 255, 0) if 200 <= pixel[0] <= 255 else pixel for pixel in stamp_img.getdata()]
    stamp_img.putdata(new_data)

    width, height = image.size

    # Calculate the font size as 5% of the image width
    font_size = int(width * 0.02)
    try:
        font_path = "font/helvetica/Helvetica.ttf"
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    base = image.copy()
    draw = ImageDraw.Draw(base)

    if signer_text:
        # Use the existing split_text_to_fit function
        lines = split_text_to_fit(signer_text, draw, width - 40, "Helvetica", font_size, context_type='image')

        # Calculate the total height of the text block
        text_height = sum(draw.textbbox((0, 0), line, font=font)[3] -
                          draw.textbbox((0, 0), line, font=font)[1] + 10 for line in lines)
        text_y_position = (height // 2) - (text_height // 2)

        # Draw each line of text
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x_position, text_y_position = calculate_position(width, height,
                                                                  text_width, bbox[3] - bbox[1], position)
            draw.text((text_x_position, text_y_position), line, font=font, fill=(255, 0, 0, 255))
            text_y_position += (bbox[3] - bbox[1]) + 10  # Adjust spacing between lines

    stamp_ratio = 0.2
    stamp_width = int(width * stamp_ratio)
    stamp_height = int(stamp_width * (stamp_img.height / stamp_img.width))
    stamp_img = stamp_img.resize((stamp_width, stamp_height), Image.LANCZOS)

    x_image_position, y_image_position = calculate_position(width, height, stamp_width, stamp_height, position)
    base.paste(stamp_img, (x_image_position, y_image_position), stamp_img)

    extension = file.filename.split('.')[-1].lower()
    if extension == 'jpg' or extension == 'jpeg':
        base = base.convert("RGB")  # Convert to RGB before saving as JPEG
        extension = 'jpeg'

    output_filename = generate_unique_filename(extension)
    output_path = os.path.join('downloads', output_filename)

    base.save(output_path, format=extension)

    return output_filename
