import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PyPDF2 import PdfReader, PdfWriter, Transformation
from PyPDF2._page import PageObject

def compute_offsets(orig_width, orig_height, scale_factor, output_width, half_height,
                    horizontal_offset, vertical_adjust, for_top=True):
    """
    Computes the translation offsets for a rotated page.
    
    After a 90° clockwise rotation:
      - The rotated page's effective width = orig_height * scale_factor
      - The rotated page's effective height = orig_width * scale_factor

    For horizontal placement:
      tx = output_width - (rotated width) + horizontal_offset
      (A positive horizontal_offset pushes the content further right.)

    For vertical placement:
      For the top half, the content is centered in [half_height, OUTPUT_PAGE_HEIGHT].
      For the bottom half, it's centered in [0, half_height].
      Then vertical_adjust is applied.
    """
    rotated_width = orig_height * scale_factor    # effective width after rotation
    rotated_height = orig_width * scale_factor      # effective height after rotation

    tx = output_width - rotated_width + horizontal_offset

    if for_top:
        ty = half_height + ((half_height - rotated_height) / 2) + vertical_adjust
    else:
        ty = ((half_height - rotated_height) / 2) + vertical_adjust

    return tx, ty

def two_pages_on_one(input_pdf_path, output_pdf_path, horizontal_offset=350, vertical_adjust=-10):
    """
    Creates an output PDF where each output page contains two consecutive pages 
    from the input PDF. For each pair, the first original page is placed in the 
    bottom half and the second in the top half (swapped positions compared to the default).
    
    Each input page is rotated 90° clockwise and scaled to fit in its half of a 
    letter-sized page (612 x 792 points). The horizontal translation (tx) is computed as:
    
      tx = OUTPUT_PAGE_WIDTH - (orig_height * scale_factor) + horizontal_offset
    
    and the vertical translation (ty) is computed based on whether the page is in the 
    top or bottom half. Adjust horizontal_offset and vertical_adjust to fine-tune the layout.
    """
    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    # Output page dimensions for Letter (points)
    OUTPUT_PAGE_WIDTH = 612
    OUTPUT_PAGE_HEIGHT = 792
    half_height = OUTPUT_PAGE_HEIGHT / 2.0

    num_pages = len(pdf_reader.pages)
    i = 0
    while i < num_pages:
        new_page = PageObject.create_blank_page(width=OUTPUT_PAGE_WIDTH, height=OUTPUT_PAGE_HEIGHT)
        
        # If there are two pages, swap their positions:
        if i + 1 < num_pages:
            # Process the first page into the bottom half
            page1 = pdf_reader.pages[i]
            orig_width1 = float(page1.mediabox.width)
            orig_height1 = float(page1.mediabox.height)
            scale_factor1 = min(
                OUTPUT_PAGE_WIDTH / orig_height1,
                half_height / orig_width1
            ) * 1.05  # 95% scale to allow margin

            tx1, ty1 = compute_offsets(orig_width1, orig_height1, scale_factor1,
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

            tx2, ty2 = compute_offsets(orig_width2, orig_height2, scale_factor2,
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

            tx, ty = compute_offsets(orig_width, orig_height, scale_factor,
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

def get_pdf_paths():
    """Opens file dialogs to get input and output PDF paths from the user."""
    tk.Tk().withdraw()  # Hide the main Tkinter window
    input_path = askopenfilename(title="Select the input PDF", filetypes=[("PDF Files", "*.pdf")])
    if not input_path:
        print("No input file selected. Exiting.")
        return None, None
    output_path = asksaveasfilename(title="Save the output PDF", defaultextension=".pdf",
                                    filetypes=[("PDF Files", "*.pdf")])
    if not output_path:
        print("No output file path selected. Exiting.")
        return None, None
    return input_path, output_path

if __name__ == "__main__":
    input_pdf, output_pdf = get_pdf_paths()
    if input_pdf and output_pdf:
        two_pages_on_one(input_pdf, output_pdf, horizontal_offset=550, vertical_adjust=-10)
        print(f"Successfully created '{output_pdf}' with swapped page positions.")
    else:
        print("Operation cancelled or invalid file paths.")