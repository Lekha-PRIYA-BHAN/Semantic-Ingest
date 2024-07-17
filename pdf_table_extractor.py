

import fitz  # import package PyMuPDF
import pandas
# https://artifex.com/blog/table-recognition-extraction-from-pdfs-pymupdf-python

# Open some document, for example a PDF (could also be EPUB, XPS, etc.)
#doc = fitz.open("cbdt/Infraon NCCM_EIMS_Infraon_NCCM_Datasheet.pdf")


def get_all_tables():
    for page in doc:
        tables = page.find_tables()
        print(f"{len(tables.tables)} table(s) on {page}")
        for table in tables:
            print(table.to_pandas())

def get_table(doc, page_no):
    page = doc[page_no]

    to_return = ""
    for table in page.find_tables():
        to_return += str(table.to_pandas()) + "\n"
    return to_return
    
        
#print(get_table(doc, 7))



exit()
# Load a desired page. This works via 0-based numbers
page = doc[8]  # this is the first page

# Look for tables on this page and display the table count
tabs = page.find_tables()
print(f"{len(tabs.tables)} table(s) on {page}")

# We will see a message like "1 table(s) on page 0 of input.pdf"

print(tabs[0].extract())

print(tabs[0].to_pandas())
print(tabs[1].to_pandas())


exit()

#pip install "camelot-py [cv]"

#git clone https://www.github.com/camelot-dev/camelot

#cd camelot

#pip install ".[cv]"

#https://camelot-py.readthedocs.io/en/master/user/install-deps.html

import camelot

#tables = camelot.read_pdf('files7/input.pdf', pages='all')
#tables = camelot.read_pdf('files7/AWSAccountManagementReferenceGuide.pdf', pages='all')
#tables = camelot.read_pdf('files7/organizations-userguide.pdf', pages='92-93', process_background=True)
tables = camelot.read_pdf('cbdt/Infraon NCCM_EIMS_Infraon_NCCM_Datasheet.pdf')

print("Total tables extracted:", tables.n)

i=1
for table in tables:
    print(table.df)
    print(table.parsing_report)
    table.to_csv("table" + str(i) + ".csv")
    i += 1

exit()

print(tables[0].df)
print(tables[0].parsing_report)
tables[0].to_csv('table1.csv')

print(tables[1].df)
print(tables[1].parsing_report)
tables[1].to_csv('table2.csv')

print(tables[2].df)
print(tables[2].parsing_report)
tables[2].to_csv('table3.csv')