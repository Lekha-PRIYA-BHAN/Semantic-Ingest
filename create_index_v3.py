import os
import json
import yaml
import re

from dotenv import load_dotenv
from langchain.llms import OpenAI, AzureOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.text_splitter import MarkdownTextSplitter
from langchain.indexes import VectorstoreIndexCreator

from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.vectorstores import FAISS

from PyPDF2 import PdfReader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.document_loaders import CSVLoader
#import unstructured
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import SpacyTextSplitter
from langchain.docstore.document import Document
from langchain.document_transformers import BeautifulSoupTransformer
from langchain.text_splitter import HTMLHeaderTextSplitter
from bs4 import BeautifulSoup 
#from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import BSHTMLLoader
import builtins
import yamlloader
from delete_chunks import delete_document, get_all_documents
from pdf_loader_splitter import pdf_loader_splitter


#x=load_dotenv("./create_index_env/.env")
x=load_dotenv()

#llm = OpenAI(model_name="text-ada-001", n=2, best_of=2)
#response = llm("Tell me a joke")
#print(response)
# 
#

#This creates the index.
#The index_name=<your_choice, give some name>,
#folder_to_process=<this is where your files are kept>. This will provide all the documents that you want to index.

disallow_folder_filter_list = [".terraform", "images"]
disallow_file_filter_list = [".terraform"]

#root_path = "C:/Users/MANISHGUPTA/OneDrive - kyndryl/manish/openai/openai-cookbook/apps/langchain"
#index_name = "index6"
#folder_to_process = "files6"

def loadJSONFile(file_path):
    docs=[]
    # Load JSON file
    with open(file_path) as file:
        data = json.load(file)

    # Iterate through 'pages'
    for page in data['pages']:
        parenturl = page['parenturl']
        pagetitle = page['pagetitle']
        indexeddate = page['indexeddate']
        snippets = page['snippets']
        metadata={"title":pagetitle}

        # Process snippets for each page
        for snippet in snippets:
            index = snippet['index']
            childurl = snippet['childurl']
            text = snippet['text']
            docs.append(Document(page_content=text, metadata=metadata))
    return docs 

def get_image_links(doc):
    print(doc)
    links = re.findall("\[.*\]\(.*\)", doc.page_content)
    str = doc.metadata['source']
    link_url_prefix = "/".join(str.split("/")[:-1])
    print(">>>>>>>>>>>>>>>>>>> found link <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    link_list = []
    for link in links:
        result = re.search("\]\((.*)\).*", link)
        link_url = ""
        if result.group(1).endswith(".png") or result.group(1).endswith(".svg") or result.group(1).endswith(".jpg") or result.group(1).endswith(".PNG"):
            link_url = link_url_prefix + "/" + result.group(1)
            link_list.append(link_url)
    #print(link_list)
    return link_list

def getKnowledgeBase(file, rootFolder, folder, embeddings):
    
    tokens = file.split('.')
    extension = tokens[len(tokens)-1]
    #extension = file.split('.')[1]
    print("******************************Processing file : ", file)
    print(rootFolder, folder)
    if  extension == "txt":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for a .txt file", filepath)
        loader = TextLoader(filepath, encoding='utf8')
        documents = loader.load()
        text_splitter = CharacterTextSplitter(separator = "\n", chunk_size=1000, chunk_overlap=200, length_function = len,)
        docs = text_splitter.split_documents(documents)
        
        knowledgeBase = FAISS.from_documents(docs, embeddings)
        return knowledgeBase
    elif extension == "tfvars-old":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for a .tfvars file", filepath)
        loader = TextLoader(filepath, encoding='utf8')
        documents = loader.load()
        text_splitter = CharacterTextSplitter(separator = "\n", chunk_size=3000, chunk_overlap=0, length_function = len,)
        docs = text_splitter.split_documents(documents)
        for doc in docs:
            print("----------------- in tfvars: ", file)
            print(doc)
        
        knowledgeBase = FAISS.from_documents(docs, embeddings)
        return knowledgeBase
    elif extension == "tfvars":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for .tfvars file", filepath)
        loader = TextLoader(filepath, encoding='utf8')
        documents = loader.load()
        #print("documents ", documents)
        knowledgeBase = FAISS.from_documents(documents, embeddings)
        return knowledgeBase
    elif extension == "tf":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for .tf file", filepath)
        loader = TextLoader(filepath, encoding='utf8')
        documents = loader.load()
        #text_splitter = CharacterTextSplitter(separator = "\n", chunk_size=1000, chunk_overlap=0, length_function = len,)
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=5,
            chunk_overlap=0,
            separators = ['\n\n']
        )
        docs = text_splitter.split_documents(documents)
        
        knowledgeBase = FAISS.from_documents(docs, embeddings)
        print("created the index for : ", filepath)
        return knowledgeBase

    elif extension == "xpdf":

        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for .pdf file", filepath)
        pdf_reader = PdfReader(filepath)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=100, length_function=len)
        #text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=100, chunk_overlap=0)
        #text_splitter = SpacyTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            print("---------------------------------------\n")
            print(chunk)
        exit()

        knowledgeBase = FAISS.from_texts(chunks, embeddings)
        return knowledgeBase
    elif extension == "xxpdf":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for .pdf file", filepath)
        loader = PyPDFLoader(filepath)
        pages = loader.load_and_split()
        for page in pages:
            print(page)
        exit()
        knowledgeBase = FAISS.from_documents(pages, embeddings)
        return knowledgeBase
    elif extension == "xpdf":

        from langchain.document_loaders import PDFMinerLoader
        from langchain.document_loaders import PDFMinerPDFasHTMLLoader
        from langchain.document_loaders import PyMuPDFLoader
        from langchain.document_loaders import PDFPlumberLoader
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for .pdf file", filepath)
        loader = UnstructuredPDFLoader(filepath)
        pages = loader.load()
        for page in pages:
            print("******************************************************\n")
            print(page)
        exit()
        knowledgeBase = FAISS.from_documents(pages, embeddings)
        return knowledgeBase
    elif extension == "xxxxxxxxxxxxxxpdf":           # for pdf if you want to run with metadata only being the pdf file name
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for .pdf file", filepath)
        loader = UnstructuredPDFLoader(filepath)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
                            # Set a really small chunk size, just to show.
                            chunk_size=1000,
                            chunk_overlap=200,
                            #separators = ['\n\n']
                        )
        #docs = text_splitter.create_documents([documents[0].page_content])
        docs = text_splitter.split_documents(documents)
        #for doc in docs:
        #    print(doc)
        knowledgeBase = FAISS.from_documents(docs, embeddings)
        return knowledgeBase
    elif extension == "pdf":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        docs = pdf_loader_splitter(folder+"/", file, "images", 1000, 500)
        #print(docs)
        #exit()
        embeddings = get_embeddings()
        knowledgeBase = FAISS.from_documents(docs, embeddings)
        return knowledgeBase
    elif extension == "xmd":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase", filepath)
        loader = UnstructuredMarkdownLoader(filepath)
        documents = loader.load()
        text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)
        knowledgeBase = FAISS.from_documents(docs, embeddings)
        return knowledgeBase
    elif extension == "md":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for .md file", filepath)
        loader = TextLoader(filepath, encoding='utf8')
        documents = loader.load()
        document = documents[0].page_content
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5"),
        ]
        text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        docs = text_splitter.split_text(document)

        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=5,
            chunk_overlap=0,
            separators = ['\n\n']
        )
        docs = text_splitter.split_documents(docs)
        for doc in docs:
            #print(doc)
            doc.metadata.update({"source": filepath})
            image_links = get_image_links(doc)
            doc.metadata.update({"images": image_links})
        #for doc in docs:
        #    print(doc)
        #    print("---------------------------------------------------------------")
        knowledgeBase = FAISS.from_documents(docs, embeddings)
        return knowledgeBase
    elif extension == "doc" or extension == "docx":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase", filepath)
        
        #loader = Docx2txtLoader(filepath)
        loader = UnstructuredWordDocumentLoader(filepath, mode="elements", strategy="fast",)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(separator = "\n", chunk_size=1000, chunk_overlap=200, length_function = len,)
        docs = text_splitter.split_documents(documents)
        knowledgeBase = FAISS.from_documents(docs, embeddings)
        return knowledgeBase
    elif extension == "yaml":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        loader = yamlloader.YAMLLoader(filepath)
        docs = loader.load()
        knowledgeBase = FAISS.from_documents(docs, embeddings)
        print("In getKnowledgeBase", filepath)
        return knowledgeBase
    elif extension == "xhtml" or extension == "xhtm":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")

        #print("In getKnowledgeBase for a .txt file", filepath)
        #loader = TextLoader(filepath, encoding='utf8')
        loader = BSHTMLLoader(filepath, 'utf8')
        documents = loader.load()
        #print(documents)
        #exit()
        s = BeautifulSoup(documents[0].page_content, "html.parser")
        #print(s)
        exit()
        #documents = [Document(page_content=str(s), metadata=documents[0].metadata)]
        #print(s)
        #exit()
        bs_transformer = BeautifulSoupTransformer()
        docs_transformed = bs_transformer.transform_documents(
            documents, tags_to_extract=["p", "li", "div", "a", "img"], separator="\n"
        )
        print(docs_transformed)
        exit()
        
        headers_to_split_on = [
            ("h1", "Header1"),
        ]
        html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        html_header_splits = html_splitter.split_text(docs_transformed[0].page_content)
        for split in html_header_splits:
            print("###################Split Start#######################")
            print(split)

        chunk_size = 2000
        chunk_overlap = 100
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            #separators = ['\p']
        )
        # Split
        splits = text_splitter.split_documents(html_header_splits)
        print(len(splits))
        for split in splits:
            print("###################Split Start#######################")
            print(split)
        knowledgeBase = FAISS.from_documents(splits, embeddings)
        return knowledgeBase
    #elif extension == "csv":
    #    filepath = folder + "/" + file
    #    filepath = filepath.replace("\\", "/")
    #    loader = CSVLoader(filepath)
    elif extension == "xxhtml" or extension == "xxhtm":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        html=""
        with open(filepath, "r", encoding="utf8") as f:
            html = f.read()

        headers_to_split_on = [
            ("h1", "Header 1"),
            ("h2", "Header 2"),
            ("h3", "Header 3"),
            ("h3", "Header 4"),
        ]

        html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        html_header_splits = html_splitter.split_text(html)
        for split in html_header_splits:
            print("###################Split Start#######################")
            print(split)
        #print(html_header_splits)
        exit()
        #print("In getKnowledgeBase for a .txt file", filepath)
        #loader = TextLoader(filepath, encoding='utf8')
        loader = BSHTMLLoader(filepath, 'utf8')
        documents = loader.load()
        print(documents)
        exit()
        s = BeautifulSoup(documents[0].page_content, "html.parser")
        print(s)
        exit()
    elif extension == "html" or extension == "htm":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")

        loader = BSHTMLLoader(filepath, 'utf8')
        documents = loader.load()

        metadata = documents[0].metadata


        html=""
        with open(filepath, "r", encoding="utf8") as f:
            html = f.read()

        
            
        #print(html)
        #exit()
        headers_to_split_on = [
            ("h1", "Header 1"),
            ("h2", "Header 2"),
            ("h3", "Header 3"),
            ("h4", "Header 4"),
            #("span", "Span"),
            #("div", "Div"),
            #("p", "Paragraph"),

        ]

        html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        html_header_splits = html_splitter.split_text(html)

        temp_metadata = metadata.copy()
        metadata = {}
        for k, v in temp_metadata.items():
            if type(v) == str:
                v = v.strip()
            
            metadata.update({k:v})

        docs = []
        for split in html_header_splits:
            #print("###################Split Start#######################")
            #print(split)
            page_content = split.page_content
            page_content = re.sub("[^\S \t\n\r\f\v]",' ', page_content)
            docs.append(Document(page_content=page_content, metadata=metadata))

        for doc in docs:
            print("###################Split Start#######################")
            print(doc)
        
        exit()
        html_header_splits = docs
        chunk_size = 2000
        chunk_overlap  = 400
        is_separator_regex = False
        #chunk_size = 1000
        #chunk_overlap = 200
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            #separators = ['\n'],
            length_function=len,
            is_separator_regex=is_separator_regex,
        )
        # Split
        splits = text_splitter.split_documents(html_header_splits)
        #print(len(splits))
        title_found = False
        chunks = []
        for split in splits:
            
            if split.page_content.startswith('Title'):
                title_found = True
            if title_found:
                print("###################Split Start#######################")
                chunks.append(split)
                print(len(split.page_content.split(" ")), split)
        for split in splits:
            #print(doc)
            split.metadata.update({"source": filepath})
            image_links = get_image_links(split)
            split.metadata.update({"images": image_links})
        knowledgeBase = FAISS.from_documents(splits, embeddings)
        return knowledgeBase
    elif extension == "xxxxhtml" or extension == "xxxxhtm":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        loader = BSHTMLLoader(filepath, 'utf8')
        documents = loader.load()

        html=""
        with open(filepath, "r", encoding="utf8") as f:
            html = f.read()
            f.close()
        #print(html)

        s = BeautifulSoup(html, "html.parser")
        s = s.get_text(separator="\n")

        s = re.sub("[^\S \t\n\r\f\v]",' ',s)

        #print(s.get_text(separator="\n").replace("\u2003", " ").replace("—", " "))
        s= s.replace("�", "")


        chunk_size = 100
        chunk_overlap  = 20
        is_separator_regex = False
        #chunk_size = 1000
        #chunk_overlap = 200
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            #separators = ['\n'],
            length_function=len,
            is_separator_regex=is_separator_regex,
        )
        # Split
        splits = text_splitter.split_documents([Document(page_content=s)])
        #print(len(splits))
        title_found = False
        chunks = []
        for split in splits:
            #print("###################Split Start#######################")
            #print(len(split.page_content.split(" ")), split)
            if split.page_content.startswith('TITLE'):
                title_found = True
            if title_found:
                print("###################Split Start#######################")
                chunks.append(split)
                print(len(split.page_content.split(" ")), split)
        exit()

    else:
        print("Do not know this extension")
        print(extension)
        return ""


def get_document_names(knowledge_base):
    document_names = []
    for doc in knowledge_base.docstore._dict:
        document_names.append(str((knowledge_base.docstore._dict[doc].metadata)['source']))
    return document_names

def check_if_file_indexed(document_names, file_prefix):
    for doc_name in document_names:
        if file_prefix in doc_name:
            return True
    return False

def check_in_filter_list(folder, filters):

    for filter in filters:
        if filter in folder:
            return True
    return False


def get_embeddings():
    if os.getenv("OPENAI_DEPLOYMENT_NAME") == None:
        print("#########################OpenAI Embedding being used!!!!!")
        embeddings = OpenAIEmbeddings()
    else:
        print("#########################AZURE OpenAI Embedding being used!!!!!")
        embeddings = AzureOpenAIEmbeddings(
                    #openai_api_type="azure",
                    openai_api_key=os.getenv("OPENAI_API_KEY"),
                    #openai_api_base=os.getenv("OPENAI_API_BASE"),
                    openai_api_version=os.getenv("OPENAI_API_VERSION"),
                    azure_deployment=os.getenv("OPENAI_DEPLOYMENT_NAME"),
                    model=os.getenv("OPENAI_MODEL_NAME"),
                )
    return embeddings

def create_index(root_path, index_name, document_folder):
    root_folder = root_path + "/" + document_folder
    print("create_index")
    print(root_folder, index_name, document_folder)
    embeddings = get_embeddings()
    try:
        db = FAISS.load_local(root_path + "/" + index_name, embeddings)
        print("Total Documents in Index at start = ", len(get_all_documents(db)))
        filesInIndex = get_document_names(db)
        for file in filesInIndex:
            print("to process:     ", file)
            #print("to process     :", root_path + "/" + file)
            #print("file exists status : ", os.path.isfile(root_path + "/" + file))
            if not os.path.isfile(root_path + "/" + file) and not os.path.isfile(file):
                delete_document(db, file, root_path + "/" + index_name)
                print("deleted:   ", root_path + "/" + file)
        print("Total Documents after removal of deleted documents = ", len(get_all_documents(db)))
                
    except:
        print("No index exists")
        filesInIndex = []

    for dirpath, dirnames, filenames in os.walk(root_folder):
        #print(dirpath, dirnames, filenames)

        #files = os.listdir(folder)
        folder = dirpath
        files = filenames

        
        listToProcess = []
        if not check_in_filter_list(folder, disallow_folder_filter_list):
            for file in files:
                fullpath_file = folder + "/" + file
                fullpath_file = fullpath_file.replace("\\", "/")
                #print(fullpath_file)
                if not check_if_file_indexed(filesInIndex, file) and not check_in_filter_list(file, disallow_file_filter_list):
                    listToProcess.append([file, fullpath_file])

        if listToProcess != []:
            print("<><><>to process the following files<><><>")
            print(listToProcess)

        #embeddings = get_embeddings()
        persist_directory = 'db'
        db = None

        combinedIndexExists = False
        for item in listToProcess:
            print("***********************************************************Processing : ", item)
            try:
                print("from db")
                db = FAISS.load_local(root_path + "/" + index_name, embeddings)
                combinedIndexExists = True
            except:
                print("exception occurred")
                
                #loader = TextLoader(item, encoding='utf8')
                knowledgeBase = getKnowledgeBase(item[0], root_folder, folder, embeddings)
                if knowledgeBase != "":
                    print("Creating a local copy of the index")
                    knowledgeBase.save_local(root_path + "/" + index_name)
                    print("Total Documents after addition of new document = ", len(get_all_documents(knowledgeBase)))
                
            if combinedIndexExists == True:
                knowledgeBase = getKnowledgeBase(item[0], root_folder, folder, embeddings)
                if knowledgeBase != "":
                    combinedIndex = FAISS.load_local(root_path + "/" + index_name, embeddings)
                    combinedIndex.merge_from(knowledgeBase)
                    combinedIndex.save_local(root_path + "/" + index_name)
                    print("Total Documents after addition of new document = ", len(get_all_documents(combinedIndex)))
                    
                
ROOT_PATH=os.getenv("ROOT_PATH")
INDEX_NAME=os.getenv("INDEX_NAME")
FOLDER_TO_INDEX=os.getenv("FOLDER_TO_INDEX")

print("Processing:",  ROOT_PATH, INDEX_NAME, FOLDER_TO_INDEX)

create_index(ROOT_PATH, INDEX_NAME, FOLDER_TO_INDEX)

