import PyPDF2
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

def merge_pdfs(pdf_paths, output_path):
    merger = PyPDF2.PdfMerger()  # for older versions, use PdfFileMerger()
    for pdf in pdf_paths:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()

if __name__ == "__main__":
    # Optional: use a file dialog to select PDFs sequentially
    Tk().withdraw()  # Hides the small tkinter window
    pdf_paths = askopenfilenames(title='Select PDF files to merge', filetypes=[('PDF Files', '*.pdf')])
    
    if pdf_paths:
        merge_pdfs(pdf_paths, "merged.pdf")
        print("Merged PDF saved as 'merged.pdf'.")
    else:
        print("No PDF files selected.")
