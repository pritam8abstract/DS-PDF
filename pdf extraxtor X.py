# Import necessary libraries:
# - PyPDF2 for PDF reading and writing.
# - Tkinter’s file dialogs to let the user select files.
import PyPDF2
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

# Hide the default Tkinter window since we only need the file dialogs.
Tk().withdraw()

# -------------------- File Selection --------------------
# Open a file dialog for the user to select a PDF file.
input_pdf_path = askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
if not input_pdf_path:
    print("No file selected.")
    exit()

# -------------------- User Input for Page Range --------------------
# Ask the user to enter the start and end page numbers.
# We use 1-indexed numbering for user convenience.
a = int(input("Enter start page number (a): "))
b = int(input("Enter end page number (b): "))

# -------------------- PDF Reading and Page Extraction --------------------
# Open the selected PDF file in binary read mode.
with open(input_pdf_path, "rb") as pdf_file:
    # Create a PdfReader object to read the PDF file.
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # Create a PdfWriter object that will be used to write selected pages.
    pdf_writer = PyPDF2.PdfWriter()

    # Validate the page range.
    # Total pages in the PDF are determined by the length of pdf_reader.pages.
    total_pages = len(pdf_reader.pages)
    if a < 1 or b > total_pages or a > b:
        print("Invalid page range.")
        exit()

    # Loop through the specified page range.
    # Since Python uses 0-based indexing, we subtract 1 from 'a'.
    for page_num in range(a - 1, b):
        # Extract the page from the original PDF.
        page = pdf_reader.pages[page_num]
        # Add the extracted page to our PdfWriter object.
        pdf_writer.add_page(page)

# -------------------- Saving the New PDF --------------------
# Open a file dialog for the user to choose where to save the new PDF.
output_pdf_path = asksaveasfilename(defaultextension=".pdf",
                                    filetypes=[("PDF files", "*.pdf")],
                                    title="Save extracted PDF as")
if output_pdf_path:
    # Write the selected pages into a new PDF file.
    with open(output_pdf_path, "wb") as output_pdf_file:
        pdf_writer.write(output_pdf_file)
    print(f"PDF pages from {a} to {b} have been saved to {output_pdf_path}.")
else:
    print("No output file selected, operation cancelled.")
