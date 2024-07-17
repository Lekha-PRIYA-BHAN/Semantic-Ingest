#https://python.langchain.com/docs/modules/data_connection/document_loaders/pdf
import os, json
from langchain.document_loaders import PDFMinerPDFasHTMLLoader
from pdf_pdf_image_extractor import pdf_extract_images, is_true_pdf
from pdf_non_pdf_image_extractor import non_pdf_extract_images
from pdf_table_extractor_v2 import get_table




def pdf_loader_splitter(root_path, filename, images_dir, max_character_size, overlap):
    ROOT = root_path
    filename = filename
    fname = ROOT + filename

    loader = PDFMinerPDFasHTMLLoader(fname)

    data = loader.load()[0]   # entire PDF is loaded as a single Document

    # print(data)

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(data.page_content,'html.parser')

    content = soup.find_all('div')

    #print(content)
    #exit()

    import re
    cur_fs = None
    cur_text = ''
    snippets = []   # first collect all snippets that have the same font size
    for c in content:
        #print("-------------------------start----------------------------------")
        if len(cur_text) > max_character_size:
            snippets.append((cur_text,cur_fs))
            #cur_fs = fs
            cur_text = c.text
        #print(c.text)
        sp = c.find('span')
        #print(sp)
        
        if not sp:
            #print("here1")
            a = c.find('a')
            if not a:
                #print("here2")
                continue
            else:
                #print("here3")
                name = a.get('name')
                if not name:
                    #print("here4")
                    continue
                else:
                    #print("here5")
                    #print("The page is :", c.text)
                    if cur_text != '':
                        #print("here5.1")
                        snippets.append((cur_text,cur_fs))
                        #cur_text += ("<"+c.text + ">")
                        cur_text = ("<"+c.text + ">")
                    else:
                        #print("here5.2")
                        cur_text += ("<"+c.text + ">")
            #continue
        else:
            #print("here6")
            st = sp.get('style')
            if not st:
                #print("here7")
                continue
            fs = re.findall('font-size:(\d+)px',st)
            if not fs:
                #print("here8")
                if c.text != '':
                    cur_text += ("\n"+c.text)
                continue
            fs = int(fs[0])
            if not cur_fs:
                #print("here9")
                cur_fs = fs
            
            if fs == cur_fs:
                #print("here10")
                cur_text += ("\n"+c.text)
            else:
                #print("here11")
                snippets.append((cur_text,cur_fs))
                cur_fs = fs
                cur_text = c.text
        #print("###########")
        #print(snippets)
        #exit()

    snippets.append((cur_text,cur_fs))
    #for snippet in snippets:
    #    print("###########################  snippet  #################################")
    #    print(len(snippet[0]))
    #    print(snippet)
    #exit()
    # Note: The above logic is very straightforward. One can also add more strategies such as removing duplicate snippets (as
    # headers/footers in a PDF appear on multiple pages so if we find duplicates it's safe to assume that it is redundant info)

    print("-----------------data metadata-----------------------")
    print(data.metadata)
    from langchain.docstore.document import Document
    cur_idx = -1
    semantic_snippets = []
    # Assumption: headings have higher font size than their respective content
    for s in snippets:
        # if current snippet's font size > previous section's heading => it is a new heading
        #print(s)
        #print("--------------1-------------------")
        #print(semantic_snippets)
        #print("###################")
        #print(s)
        if not semantic_snippets or s[1] == None or semantic_snippets[cur_idx].metadata['heading_font'] == None or s[1] > semantic_snippets[cur_idx].metadata['heading_font']:
            if len(s[0]) < 21:
                metadata={'heading':s[0], 'content_font': 0, 'heading_font': s[1]}
                metadata.update(data.metadata)
                semantic_snippets.append(Document(page_content='',metadata=metadata))
            else:
                metadata={'heading':'', 'content_font': s[1], 'heading_font': 0}
                metadata.update(data.metadata)
                semantic_snippets.append(Document(page_content=s[0],metadata=metadata))
            cur_idx += 1
            continue
        #print("--------------2-------------------")
        # if current snippet's font size <= previous section's content => content belongs to the same section (one can also create
        # a tree like structure for sub sections if needed but that may require some more thinking and may be data specific)
        if (len(semantic_snippets[cur_idx].page_content) < max_character_size and "<Page" not in s[0] and
              (not semantic_snippets[cur_idx].metadata['content_font'] 
               or s[1] <= semantic_snippets[cur_idx].metadata['content_font'])
            ):
            semantic_snippets[cur_idx].page_content += s[0]
            semantic_snippets[cur_idx].metadata['content_font'] = max(s[1], semantic_snippets[cur_idx].metadata['content_font'])
            continue
        #print("--------------3-------------------")
        # if current snippet's font size > previous section's content but less than previous section's heading than also make a new
        # section (e.g. title of a PDF will have the highest font size but we don't want it to subsume all sections)
        metadata={'heading':s[0], 'content_font': 0, 'heading_font': s[1]}
        metadata.update(data.metadata)
        semantic_snippets.append(Document(page_content='',metadata=metadata))
        cur_idx += 1
        #print("--------------4-------------------")
        #exit()

    #for snippet in semantic_snippets:
    #    print("###################### SNIPPET ############################")
    #    print(len(snippet.page_content))
    #    print(snippet)
    #exit()

    # Remove all the page tags we had put earlier
    # add another key called 'pages' in the snippet's metadata
    prev_pg='1'
    for snippet in semantic_snippets:
        #print(str(snippet))
        #print("-----------------------------------------------")
        res = re.findall("<Page (\d+)>", str(snippet))
        #print(res)
        if not res:
            res = [prev_pg]
        res.sort()
        #print(res)
        for num in res:
            snippet.page_content = snippet.page_content.replace('<Page '+num+'>', '')
            #snippet.metadata = json.loads(str(snippet.metadata).replace('<Page '+num+'>', ''))
            for key in snippet.metadata.keys():
                if type(snippet.metadata[key]) == str and '<Page ' in snippet.metadata[key]:
                    X = snippet.metadata[key].replace('<Page '+num+'>', '')
                    snippet.metadata[key] = X
            #X = str(snippet.metadata).replace('<Page '+num+'>', '')
            #X = X.replace("'", "\"")
            #print(X)
            #snippet.metadata = X
        snippet.metadata["pages"] = res
        #print(str(snippet))
        if len(res)>0:
            prev_pg = res[len(res)-1]

    # remove snippets that have empty page_content
    temp_snippets = semantic_snippets
    semantic_snippets = []
    for snippet in temp_snippets:
        if snippet.page_content != '':
            semantic_snippets.append(snippet)
    
    
    # Print for testing purposes
    #for snippet in semantic_snippets:
    #    print("###################### SNIPPET ############################")
    #    print(len(snippet.page_content))
    #    print(snippet)
    #exit()

    if is_true_pdf(ROOT, filename):
        image_paths = pdf_extract_images(ROOT, filename, "html", images_dir)
    else:
        image_paths = non_pdf_extract_images(ROOT, filename, "html", images_dir)
        
    #print("Finished extracting the images")
    for snippet in semantic_snippets:
        for image_path in image_paths:
            if image_path[0] in snippet.metadata["pages"]:
                if "images" not in snippet.metadata.keys():
                    snippet.metadata["images"] = []
                snippet.metadata["images"] += image_path[1]
        

    # perform overlap
    temp_snippets = semantic_snippets
    semantic_snippets = []
    isFirst=True
    title=""
    prev_snippet=""
    for snippet in temp_snippets:
        if isFirst:
            title=snippet.page_content
            isFirst = False
        else:
            snippet.metadata['heading'] = title + "\n" + snippet.metadata['heading']
            overlap_str = snippet.page_content[:min(overlap, len(snippet.page_content))]
            prev_snippet.page_content = prev_snippet.page_content + "\n" + overlap_str
            snippet.page_content = title + snippet.page_content
            #print("------------------------")
            #print(overlap_str)
            
        prev_snippet = snippet
        semantic_snippets.append(snippet)
        #print("###################### SNIPPET ############################")
        #print(len(snippet.page_content))
        #print(snippet)


    #Insert the tables as separate chunks
    tables_snippets = []
    page_number_seen = 0
    tables_seen = ""
    prefix = ""
    for snippet in semantic_snippets:
        #if 'pages' in snippet.metadata.keys():
        pages = snippet.metadata["pages"]
        for page in pages:
            if int(page) > int(page_number_seen):
                
                #print("page being analyzed: ", page)
                tables = get_table(fname, page_number_seen)
                tables_seen = ""
                prefix = ""
                if tables != "":
                    new_snippet = snippet.copy()
                    tables_seen = tables
                    prefix = prefix + "\n" + snippet.metadata["heading"]
                    new_snippet.page_content = prefix + tables_seen
                    tables_snippets.append(new_snippet)
                page_number_seen += 1
            elif int(page) == int(page_number_seen):
                if tables_snippets != []:
                    if page in tables_snippets[len(tables_snippets)-1].metadata['pages']:
                        
                        prefix = prefix + "\n" + snippet.metadata["heading"]
                        tables_snippets[len(tables_snippets)-1].page_content = prefix + tables_seen




    semantic_snippets = semantic_snippets + tables_snippets

    for snippet in semantic_snippets:
        print("###################### SNIPPET ############################")
        print(snippet)

    return semantic_snippets





#pdf_loader_splitter("./files7/", "AWSAccountManagementReferenceGuide.pdf", "images")
#pdf_loader_splitter("./files7/", "organizations-userguide.pdf", "images")
#pdf_loader_splitter("./files7/", "organizing-your-aws-environment.pdf", "images")
#pdf_loader_splitter("./files7/", "OU hierarchy for BFSI - Kyndryl Consult Cloud Practice.pdf", "images")
#pdf_loader_splitter("./cbdt/", "Cisco 82000 Data Sheet_nb-06-cat8200-series-edge-plat-ds-cte-en.pdf", "images", 1000)
#pdf_loader_splitter("./cbdt/", "Trobleshoot SDWAN control connection_214509-troubleshoot-control-connections.pdf", "images", 1000)

#pdf_loader_splitter("./cbdt/", "Infraon NCCM_EIMS_Infraon_NCCM_Datasheet.pdf", "images", 1000, 500)
#pdf_loader_splitter("./cbdt/", "Cisco 8500 Series Data Sheet_datasheet-c78-744089.pdf", "images", 1000, 500)
#pdf_loader_splitter("./investment_reports/", "the-great-inflection-point-a-look-into-the-future-of-cars.pdf", "images", 1000, 500)
