

import pymupdf4llm
# Extract the PDF content as Markdown
file_path = "/Users/michasmi/code/scripts/assets/PIMCO-3.6.1.9.3 Markit Digital Addendum_fullysigned_09252017.pdf"


md_text_words = pymupdf4llm.to_markdown(
    doc=file_path,
    pages=[0, 1, 2],
    page_chunks=False,
    write_images=False,
    # image_path="images",
    # image_format="png",
    # dpi=300,
    extract_words=True
)

import pathlib
output_file = pathlib.Path("output.md")
output = ''
with open (output_file, 'w') as f:
    for dict in md_text_words:
        output = f"{output}\n{dict.get('text', '')}"
    f.write(output)
    