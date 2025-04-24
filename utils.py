import base64
import io
from PIL import Image
import pdf2image

#Convert uploaded PDF to image
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:

        ## Convert the PDf to image
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]

        #convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [

            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode() #encode to base 64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")