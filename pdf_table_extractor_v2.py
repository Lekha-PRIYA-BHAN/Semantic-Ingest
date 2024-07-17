import fitz  # import package PyMuPDF
# https://artifex.com/blog/table-recognition-extraction-from-pdfs-pymupdf-python
# https://towardsdatascience.com/extracting-text-from-pdf-files-with-python-a-comprehensive-guide-9fc4003d517

# Open some document, for example a PDF (could also be EPUB, XPS, etc.)


def get_doc(path):
    return fitz.open(path)

def get_all_tables():
    for page in doc:
        tables = page.find_tables()
        print(f"{len(tables.tables)} table(s) on {page}")
        for table in tables:
            print(table.to_pandas())

def get_table(path, page_no):
    doc = get_doc(path)
    page = doc[page_no]

    to_return = ""
    for table in page.find_tables():
        try:
            to_return += (str(table.to_pandas()) + "\n")
        except:
            pass
    return to_return
    
#doc = fitz.open("cbdt/Infraon NCCM_EIMS_Infraon_NCCM_Datasheet.pdf")
#print(get_table(doc, 7))