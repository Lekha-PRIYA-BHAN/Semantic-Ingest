import os
import fitz
import sys, pathlib
import re
# https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/extract-images/extract-from-pages.py
# https://pymupdf.readthedocs.io/en/latest/recipes-images.html#how-to-extract-images-pdf-documents


def is_true_pdf(root_path, filename):
    print("--------------Testing if a True PDF file------------------")
    ROOT = root_path
    fname = ROOT + filename
    # Open the PDF
    doc = fitz.open(fname)

    #for method in dir(doc):
    #    if callable(getattr(doc, method)):
    #        print(method)
    

    if len(doc) == 1:
        return True
    else:
        for page in doc:
            images1 = page.get_images()
            d = page.get_text("dict")
            blocks = d["blocks"]  # the list of block dictionaries
            images2 = [b for b in blocks if b["type"] == 1]
            if len(images1) > len(images2):
                return True
            else:
                return False



def list_files(directory):
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        # Check if it's a file and not a directory
        if os.path.isfile(filepath):
            print(filepath)
            print(is_true_pdf(directory, filename))

# Example usage
#directory_path = './files7/'
#list_files(directory_path)



def pdf_extract_images(root_path, filename, type, images_dir):
    ROOT = root_path
    #type = "html"
    if not os.path.exists(root_path + images_dir):
        os.makedirs(root_path + images_dir)
    fname = ROOT + filename
    #image_template="""<p><img src="{image_path}"/></p>"""
    image_template="""{image_path}"""

    image_file_prefix=filename.split(".")[len(filename.split("."))-2]

    #reader = fitz.open(ROOT + )

    #with fitz.open(fname) as doc:  # open document
    #    html = chr(12).join([page.get_text(type) for page in doc])

    doc = fitz.open(fname)
    html = ""
    i=1
    image_relative_paths=[]
    for page in doc:
        images = page.get_images()
        #images = doc.getPageImageList(i-1)
        print(page)
        print(len(images))
        #print(images)
 
        img_filenames = []
        for image in images:
            xref = image[0]
            #print(image[0])
            #print(fitz.Pixmap(doc, image[0]))
            img = doc.extract_image(xref) # using the xref
            img_data = img["image"]
            img_filename = ROOT + images_dir + "/" + image_file_prefix + "_" + str(xref) + "." + img["ext"]
            image_relative_paths.append([str(i), [img_filename]])
            if img_filename not in img_filenames:
                img_filenames.append(img_filename)
                fout = open(img_filename, "wb")
                fout.write(img_data)
                fout.close()
        to_replace = "page"+str(i)
        sub_html = page.get_text(type)
        sub_html = str(sub_html.replace("page0", to_replace))
        s=str(re.escape("<img style"))
        e=str(re.escape(">"))
        res = re.findall(r"<img(?s:.*?)>", sub_html)
        #print("------------------------------------------START---------------------------------------------------")
        #print(sub_html)
        #print("##############################")
        #print(res)
        for img in res:
            try:
                img_filename = img_filenames.pop(0)
                sub_html = sub_html.replace(img, image_template.format(image_path=img_filename))
            except:
                image_filename = ""
                sub_html = sub_html.replace(img, "")
        #print(sub_html.find("<img style"))
        page_no = "page" + str(i) + "\n"
        sub_html = page_no + sub_html
        html = chr(12).join([html, sub_html])
        

        i += 1
    return image_relative_paths
        
        

    #print(html)

    #pathlib.Path(fname + ".html").write_text(html)

#images = pdf_extract_images("./files7/", "organizing-your-aws-environment.pdf", "html", "images")
#print(images)
#pathlib.Path(fname + ".xhtml").write_bytes(html.encode())