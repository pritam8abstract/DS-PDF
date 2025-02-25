#!/usr/bin/env python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askopenfilenames
from PyPDF2 import PdfReader, PdfWriter, Transformation, PdfMerger
from PyPDF2._page import PageObject

class DSPDF:
    """
    DS PDF Application Class to handle PDF operations:
      - Create a 1x2 collage (placing two pages on one page)
      - Extract pages from a PDF
      - Merge multiple PDFs

    The code in each method is adapted from your separate modules:
      - Collage functionality from pdf colllage.py :contentReference[oaicite:3]{index=3}
      - Extraction functionality from pdf extraxtor X.py :contentReference[oaicite:4]{index=4}
      - Merge functionality from pdf join.py :contentReference[oaicite:5]{index=5}
    """

    @staticmethod
    def compute_offsets(orig_width, orig_height, scale_factor, output_width, half_height,
                        horizontal_offset, vertical_adjust, for_top=True):
        """
        Computes translation offsets for a rotated page.
        (Adapted from pdf colllage.py :contentReference[oaicite:6]{index=6})
        """
        rotated_width = orig_height * scale_factor
        rotated_height = orig_width * scale_factor
        tx = output_width - rotated_width + horizontal_offset
        if for_top:
            ty = half_height + ((half_height - rotated_height) / 2) + vertical_adjust
        else:
            ty = ((half_height - rotated_height) / 2) + vertical_adjust
        return tx, ty

    @staticmethod
    def collage_pdf(input_pdf_path, output_pdf_path, horizontal_offset=550, vertical_adjust=-10):
        """
        Creates a collage PDF where each output page contains two rotated pages from the input.
        (Adapted from pdf colllage.py :contentReference[oaicite:7]{index=7})
        """
        pdf_reader = PdfReader(input_pdf_path)
        pdf_writer = PdfWriter()

        # Define output page dimensions for a letter-sized page (points)
        OUTPUT_PAGE_WIDTH = 612
        OUTPUT_PAGE_HEIGHT = 792
        half_height = OUTPUT_PAGE_HEIGHT / 2.0

        num_pages = len(pdf_reader.pages)
        i = 0
        while i < num_pages:
            new_page = PageObject.create_blank_page(width=OUTPUT_PAGE_WIDTH, height=OUTPUT_PAGE_HEIGHT)
            
            if i + 1 < num_pages:
                # Process the first page into the bottom half
                page1 = pdf_reader.pages[i]
                orig_width1 = float(page1.mediabox.width)
                orig_height1 = float(page1.mediabox.height)
                scale_factor1 = min(
                    OUTPUT_PAGE_WIDTH / orig_height1,
                    half_height / orig_width1
                ) * 1.05

                tx1, ty1 = DSPDF.compute_offsets(orig_width1, orig_height1, scale_factor1,
                                                   OUTPUT_PAGE_WIDTH, half_height,
                                                   horizontal_offset, vertical_adjust,
                                                   for_top=False)
                trans1 = (Transformation()
                          .rotate(90)
                          .scale(scale_factor1, scale_factor1)
                          .translate(tx1, ty1))
                page1.add_transformation(trans1)
                new_page.merge_page(page1)

                # Process the second page into the top half
                page2 = pdf_reader.pages[i + 1]
                orig_width2 = float(page2.mediabox.width)
                orig_height2 = float(page2.mediabox.height)
                scale_factor2 = min(
                    OUTPUT_PAGE_WIDTH / orig_height2,
                    half_height / orig_width2
                ) * 1.05

                tx2, ty2 = DSPDF.compute_offsets(orig_width2, orig_height2, scale_factor2,
                                                   OUTPUT_PAGE_WIDTH, half_height,
                                                   horizontal_offset, vertical_adjust,
                                                   for_top=True)
                trans2 = (Transformation()
                          .rotate(90)
                          .scale(scale_factor2, scale_factor2)
                          .translate(tx2, ty2))
                page2.add_transformation(trans2)
                new_page.merge_page(page2)
            else:
                # If only one page remains, place it in the bottom half.
                page = pdf_reader.pages[i]
                orig_width = float(page.mediabox.width)
                orig_height = float(page.mediabox.height)
                scale_factor = min(
                    OUTPUT_PAGE_WIDTH / orig_height,
                    half_height / orig_width
                ) * 1.05

                tx, ty = DSPDF.compute_offsets(orig_width, orig_height, scale_factor,
                                                 OUTPUT_PAGE_WIDTH, half_height,
                                                 horizontal_offset, vertical_adjust,
                                                 for_top=False)
                trans = (Transformation()
                         .rotate(90)
                         .scale(scale_factor, scale_factor)
                         .translate(tx, ty))
                page.add_transformation(trans)
                new_page.merge_page(page)
            
            pdf_writer.add_page(new_page)
            i += 2

        with open(output_pdf_path, "wb") as out_file:
            pdf_writer.write(out_file)

    @staticmethod
    def extract_pages(input_pdf_path, start_page, end_page, output_pdf_path):
        """
        Extracts pages from a PDF (using 1-indexed page numbers) and saves them as a new PDF.
        (Adapted from pdf extraxtor X.py :contentReference[oaicite:8]{index=8})
        """
        with open(input_pdf_path, "rb") as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            pdf_writer = PdfWriter()

            total_pages = len(pdf_reader.pages)
            if start_page < 1 or end_page > total_pages or start_page > end_page:
                raise ValueError("Invalid page range.")

            for page_num in range(start_page - 1, end_page):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)

        with open(output_pdf_path, "wb") as output_pdf_file:
            pdf_writer.write(output_pdf_file)

    @staticmethod
    def merge_pdfs(pdf_paths, output_path):
        """
        Merges multiple PDFs into a single PDF.
        (Adapted from pdf join.py :contentReference[oaicite:9]{index=9})
        """
        merger = PdfMerger()
        for pdf in pdf_paths:
            merger.append(pdf)
        merger.write(output_path)
        merger.close()

def main():
    """
    Provides a simple command-line interface for DS PDF operations.
    This can be later replaced by a Flask route for web-based usage.
    """
    print("Welcome to DS PDF App")
    print("Select an operation:")
    print("1. Create a collage of PDF pages (1x2 collage)")
    print("2. Extract pages from a PDF")
    print("3. Merge multiple PDFs")
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    # Hide the Tkinter root window
    tk.Tk().withdraw()

    if choice == '1':
        input_pdf = askopenfilename(title="Select the input PDF for collage", filetypes=[("PDF Files", "*.pdf")])
        if not input_pdf:
            print("No input file selected. Exiting.")
            return
        output_pdf = asksaveasfilename(title="Save the collaged PDF", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not output_pdf:
            print("No output file selected. Exiting.")
            return
        try:
            DSPDF.collage_pdf(input_pdf, output_pdf)
            print(f"Collaged PDF created successfully at: {output_pdf}")
        except Exception as e:
            print("An error occurred while creating the collage:", e)

    elif choice == '2':
        input_pdf = askopenfilename(title="Select the PDF for extraction", filetypes=[("PDF Files", "*.pdf")])
        if not input_pdf:
            print("No input file selected. Exiting.")
            return
        try:
            start_page = int(input("Enter start page number: "))
            end_page = int(input("Enter end page number: "))
        except ValueError:
            print("Invalid page number input. Exiting.")
            return
        output_pdf = asksaveasfilename(title="Save the extracted PDF", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not output_pdf:
            print("No output file selected. Exiting.")
            return
        try:
            DSPDF.extract_pages(input_pdf, start_page, end_page, output_pdf)
            print(f"Extracted PDF created successfully at: {output_pdf}")
        except Exception as e:
            print("An error occurred while extracting pages:", e)

    elif choice == '3':
        pdf_files = askopenfilenames(title="Select PDF files to merge", filetypes=[("PDF Files", "*.pdf")])
        if not pdf_files:
            print("No PDF files selected. Exiting.")
            return
        output_pdf = asksaveasfilename(title="Save the merged PDF", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not output_pdf:
            print("No output file selected. Exiting.")
            return
        try:
            DSPDF.merge_pdfs(pdf_files, output_pdf)
            print(f"Merged PDF created successfully at: {output_pdf}")
        except Exception as e:
            print("An error occurred while merging PDFs:", e)
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
