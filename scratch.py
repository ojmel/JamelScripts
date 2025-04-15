import os

# import pandas as pd
# from PyPDF2 import PdfReader, PdfWriter

# Define the paths to your PDFs
# source_pdf_path = 'source.pdf'  # PDF from which to extract the first page
# target_pdf_path = 'target.pdf'  # PDF to which the first page will be merged
# output_pdf_path = 'output.pdf'  # Path for the merged output
# nano_dir=r'C:\Research\nanosight'
# pdf_writer = PdfWriter()
# for file in os.listdir(nano_dir):
#     full_file=os.path.join(nano_dir,file)
#     first_page=PdfReader(full_file).pages[0]
#     pdf_writer.add_page(first_page)

# Create PdfReader objects for both source and target PDFs
# source_pdf =
# target_pdf = PdfReader(target_pdf_path)

# Extract the first page from the source PDF
# first_page = source_pdf.pages[0]

# Add all pages from the target PDF to the PdfWriter
# for page in target_pdf.pages:
#     pdf_writer.add_page(page)

# Write the output PDF to a file
# with open(output_pdf_path, 'wb') as output_pdf_file:
#     pdf_writer.write(output_pdf_file)
#
# print(f"First page from '{source_pdf_path}' merged into '{target_pdf_path}' and saved as '{output_pdf_path}'.")

# a=pd.read_html('https://www.thonky.com/qr-code-tutorial/log-antilog-table')[1]
# a.dtypes()//
# print({key: value for key, value in zip(a['Integer.1'], a['Exponent of ɑ.1'])})

import socket
try:
    with socket.create_connection(('73.251.37.65',5005)):
        print(123)
except Exception as e:
    print('failed')
