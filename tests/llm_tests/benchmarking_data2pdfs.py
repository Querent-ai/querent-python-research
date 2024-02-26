# import pandas as pd
# from fpdf import FPDF
# import os

# # Create the directory for PDF files if it doesn't already exist
# output_dir = "pdfs"
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)

# def create_pdf_with_text(text: str, file_path: str):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
#     pdf.set_font('DejaVu', size=12)
#     pdf.multi_cell(0, 10, text)
#     pdf.output(file_path)

# csv_file_path = "web_nlg_extract.csv"
# line_counter = 0
# max_lines = 1000

# for chunk in pd.read_csv(csv_file_path, chunksize=500):
#     for index, row in chunk.iterrows():
#         if line_counter >= max_lines:
#             break

#         # Fetch the text for the current row
#         text = str(row.get("original text", ""))
        
#         # Define the output path for the current PDF
#         output_pdf_path = os.path.join(output_dir, f"{line_counter + 1}.pdf")
        
#         # Create a PDF with the text
#         create_pdf_with_text(text, output_pdf_path)
        
#         # Increment the line counter
#         line_counter += 1

#     if line_counter >= max_lines:
#         break

# print(f"{line_counter} PDFs saved successfully in the directory '{output_dir}'.")