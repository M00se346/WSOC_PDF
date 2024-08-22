import os
import PyPDF2
from PIL import Image
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def extract_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        num_pages = reader.numPages
        text_content = []

        for page_num in range(num_pages):
            page = reader.getPage(page_num)
            text_content.append(page.extract_text())
        
    return text_content

def extract_images(pdf_path):
    images = []
    pdf_doc = PyPDF2.PdfFileReader(open(pdf_path, 'rb'))

    for page_num in range(pdf_doc.numPages):
        page = pdf_doc.getPage(page_num)
        xObject = page['/Resources']['/XObject'].getObject()

        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj].getData()
                mode = ""
                if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                    mode = "RGB"
                else:
                    mode = "P"

                if '/Filter' in xObject[obj]:
                    if xObject[obj]['/Filter'] == '/FlateDecode':
                        mode = 'P'
                        img = Image.frombytes(mode, size, data)
                        images.append((img, obj))
                    elif xObject[obj]['/Filter'] == '/DCTDecode':
                        mode = 'RGB'
                        img = Image.open(io.BytesIO(data))
                        images.append((img, obj))
                    elif xObject[obj]['/Filter'] == '/JPXDecode':
                        mode = 'RGB'
                        img = Image.open(io.BytesIO(data))
                        images.append((img, obj))
                    elif xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                        mode = 'L'
                        img = Image.open(io.BytesIO(data))
                        images.append((img, obj))
                else:
                    img = Image.frombytes(mode, size, data)
                    images.append((img, obj))

    return images

def create_pdf(output_path, text_content, images):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    for text in text_content:
        c.setFont("Helvetica", 12)
        text = text.strip().split("\n")
        for i, line in enumerate(text):
            c.drawString(30, height - 30 - i*15, line)

    for image, obj in images:
        image_reader = ImageReader(image)
        c.drawImage(image_reader, 30, height - 200, width=200, preserveAspectRatio=True, mask='auto')
    
    c.showPage()
    c.save()

def process_pdfs(pdf_dir, output_pdf):
    all_text_content = []
    all_images = []

    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, pdf_file)
            text_content = extract_text(pdf_path)
            images = extract_images(pdf_path)
            all_text_content.extend(text_content)
            all_images.extend(images)
    
    create_pdf(output_pdf, all_text_content, all_images)
    print("Compiled document created at: {}".format(output_pdf))


if __name__ == "__main__":
    pdf_directory = "pdfs"  # Directory containing the PDFs
    output_pdf_path = "output/compiled_document.pdf"  # Output path for the compiled PDF

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    process_pdfs(pdf_directory, output_pdf_path)

