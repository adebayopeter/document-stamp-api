# PDF Stamping Flask API

This Flask API allows you to stamp PDF documents with text or images. It provides several endpoints to apply different types of stamps to your PDF files.

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [License](#license)

## Requirements

- Python 3.6+
- Flask
- PyPDF2
- reportlab
- Pillow

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/pdf-stamping-api.git
   cd pdf-stamping-api
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   
   ```sh 
   pip install -r requirements.txt 
   ```
   
## Usage

   Run the Flask application:

   ```sh
   python app.py
   ```

   The API will be available at http://127.0.0.1:5000.

   ### Endpoints
1. `/stamp`

   Description: Stamps the PDF document with the given text.

   Method: POST 

   Form Data:
   - `file`: The PDF file to be stamped.
   - `stamp`: The text to stamp on the PDF (default: "CONFIDENTIAL").
   
   Example:
   ```sh
   curl -X POST -F file=@document.pdf -F stamp="TOP SECRET" http://127.0.0.1:5000/stamp -o stamped_document.pdf
   ```
   
2. `/stamp_image`

   Description: Stamps the PDF document with the given image.

   Method: POST 

   Form Data:
   - `file`: The PDF file to be stamped.
   - `stamp_image`: The image file to use as a stamp.
   
   Example:
   ```sh
   curl -X POST -F file=@document.pdf -F stamp_image=@stamp.png http://127.0.0.1:5000/stamp_image -o stamped_document.pdf
   ```
   
3. `/stamp_image_transparent`

   Description: Stamps the PDF document with the given image, making the white pixels transparent.
   
   Method: POST 

   Form Data:
   - `file`: The PDF file to be stamped.
   - `stamp_image`: The image file to use as a stamp.
   
   Example:
   ```sh
   curl -X POST -F file=@document.pdf -F stamp_image=@stamp.png http://127.0.0.1:5000/stamp_image_transparent -o stamped_document.pdf
   ```
   
4. `/stamp_image_text`

   Description: Stamps the PDF document with the given image and adds a text indicating the signer.

   Method: POST 

   Form Data:
   - `file`: The PDF file to be stamped.
   - `stamp_image`: The image file to use as a stamp.
   - `signer_name`: The name of the signer to include in the text stamp (default: "Adebayo Olaonipekun").
   
   Example:
   ```sh
   curl -X POST -F file=@document.pdf -F stamp_image=@stamp.png -F signer_name="John Doe" http://127.0.0.1:5000/stamp_image_text -o stamped_document.pdf
   ```
   
## License
This project is licensed under [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)