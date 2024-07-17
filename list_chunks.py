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
import builtins
import yamlloader
from delete_chunks import delete_document


x=load_dotenv()

disallow_folder_filter_list = [".terraform"]
disallow_file_filter_list = [".terraform"]

def get_image_links(doc):
    links = re.findall("\[.*\]\(.*\)", doc.page_content)
    str = doc.metadata['source']
    link_url_prefix = "/".join(str.split("/")[:-1])
    print(">>>>>>>>>>>>>>>>>>> found link <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    link_list = []
    for link in links:
        result = re.search("\]\((.*)\).*", link)
        link_url = ""
        if result.group(1).endswith(".png"):
            link_url = link_url_prefix + "/" + result.group(1)
            link_list.append(link_url)
    #print(link_list)
    return link_list

def get_all_documents(knowledge_base):
    document_ids = []
    for doc in knowledge_base.docstore._dict:
        #print(doc)
        #print(knowledge_base.docstore._dict[doc].metadata)
        print("----------------------------------start--------------------------------------")
        print(knowledge_base.docstore._dict[doc])
        #get_image_links(knowledge_base.docstore._dict[doc])
        #exit()
        document_ids.append(doc)
    #print(document_ids)
    return document_ids

def get_document_names(knowledge_base):
    document_names = []
    source_set = set({})
    for doc in knowledge_base.docstore._dict:
        document_names.append(str((knowledge_base.docstore._dict[doc].metadata)['source']))
        source_set.add(str((knowledge_base.docstore._dict[doc].metadata)['source']))
    return source_set

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

def get_knowledgebase(root_path, index_name, embeddings):
    try:
        db = FAISS.load_local(root_path + "/" + index_name, embeddings)
        return db
    except:
        return ""

def list_chunks(root_path, index_name, document_folder, embeddings):
    root_folder = root_path + "/" + document_folder
    print("list chunks")
    print(root_folder, index_name, document_folder)
    try:
        db = FAISS.load_local(root_path + "/" + index_name, embeddings)
        print("Total Documents in Index at start = ", len(get_all_documents(db)))
        filesInIndex = get_document_names(db)
        print("files in Index: ", filesInIndex)
        for file in filesInIndex:
            print("to process:     ", file)
            #print("to process     :", root_path + "/" + file)
            #print("file exists status : ", os.path.isfile(root_path + "/" + file))
            if not os.path.isfile(root_path + "/" + file) and not os.path.isfile(file):
                #delete_document(db, file, root_path + "/" + index_name)
                print("deleted:   ", root_path + "/" + file)
        print("Total Documents after removal of deleted documents = ", len(get_all_documents(db)))
                
    except:
        print("No index exists")
        filesInIndex = []


ROOT_PATH="C:/Users/MANISHGUPTA/OneDrive - kyndryl/manish/openai/openai-cookbook/apps/langchain"
INDEX_NAME="arch_index"
FOLDER_TO_INDEX="arch"
embeddings = OpenAIEmbeddings(openai_api_type="azure",
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                openai_api_base=os.getenv("OPENAI_API_BASE"),
                deployment=os.getenv("OPENAI_DEPLOYMENT_NAME"),
                model=os.getenv("OPENAI_MODEL_NAME"))
#list_chunks(ROOT_PATH, INDEX_NAME, FOLDER_TO_INDEX, embeddings)
source_set = get_document_names(get_knowledgebase(ROOT_PATH, INDEX_NAME, embeddings))
source_string = ""
if source_set != {}:
    source_string = " , ".join(source_set)
if source_string != "":
    tokens = source_string.split(",")
    for token in tokens:
        print(token.strip())


