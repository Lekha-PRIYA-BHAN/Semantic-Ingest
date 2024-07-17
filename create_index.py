import os
import json
import yaml

from dotenv import load_dotenv
from langchain.llms import OpenAI
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
#import unstructured
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import SpacyTextSplitter
from langchain.docstore.document import Document
import builtins
import yamlloader


x=load_dotenv()

#llm = OpenAI(model_name="text-ada-001", n=2, best_of=2)
#response = llm("Tell me a joke")
#print(response)
# 
#

#This creates the index.
#The index_name=<your_choice, give some name>,
#bookeeping_filename=<your choice, give some name>,
#folder_to_process=<this is where your files are kept>. This will provide all the documents that you want to index.

index_name = "index1"
bookeeping_filename = "./tests/combined1.txt"
folder_to_process = "./tests/files1"

index_name = "index2"
bookeeping_filename = "combined2.txt"
folder_to_process = "files2"

index_name = "index1"
bookeeping_filename = "combined.txt"
folder_to_process = "files"



index_name = "index3"
bookeeping_filename = "combined3.txt"
folder_to_process = "files3"
bookeeping_dir = "bookeeping3"

index_name = "index4"
bookeeping_filename = "combined4.txt"
folder_to_process = "/app/ingest/files1"
bookeeping_dir = "bookeeping4"


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


def getKnowledgeBase(file, rootFolder, folder, embeddings):
    tokens = file.split('.')
    extension = tokens[len(tokens)-1]
    #extension = file.split('.')[1]
    print("******************************Processing file : ", file)
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
    elif extension == "xpdf":
        filepath = folder + "/" + file
        filepath = filepath.replace("\\", "/")
        print("In getKnowledgeBase for .pdf file", filepath)
        loader = PyPDFLoader(filepath)
        pages = loader.load_and_split()
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
            print(page.page_content)
        exit()
        knowledgeBase = FAISS.from_documents(pages, embeddings)
        return knowledgeBase
    elif extension == "pdf":           
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
        #for doc in docs:
        #    print(doc.page_content)
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
    else:
        print("Do not know this extension")
        print(extension)
        return ""


def record_doc_2_embeddings(bookeeping_dir, folder, doc_file_name, knowledgebase, dirnames, bookeeping_filename):

    #for dir in dirnames:
    #    os.mkdir(dir)

    book_keeper = bookeeping_dir + "/" + bookeeping_dir + "_file.txt"
    with open(book_keeper, "a+") as f:
        embeddings = knowledgebase.index_to_docstore_id
        f.write(doc_file_name+":")
        json.dump(embeddings, f)
        f.write("\n")

    #if os.path.isfile(bookeeping_dir + "/" + doc_file_name + ".txt"):
    #    print("File already exists")
    #else:
    #    with open(bookeeping_dir + "/" + doc_file_name + ".txt", "a+") as f:
    #        print("created file")
    #        
    #        embeddings = knowledgebase.index_to_docstore_id
    #        print(type(embeddings))
    #        json.dump(embeddings, f)




try:
    os.mkdir(bookeeping_dir)
except:
    #print the exception
    pass
root_folder = folder_to_process
for dirpath, dirnames, filenames in os.walk(root_folder):
    #print(dirpath, dirnames, filenames)

    #files = os.listdir(folder)
    folder = dirpath
    files = filenames
    # create the file if not already done
    combined = open(bookeeping_filename,"a+")
    combined.close()
    with open(bookeeping_filename) as f:
        combinedFiles = f.read().splitlines()
    #print(combinedFiles)

    listToProcess = []
    for file in files:
        fullpath_file = folder + "/" + file
        fullpath_file = fullpath_file.replace("\\", "/")
        #print(fullpath_file)
        if fullpath_file not in combinedFiles:
            listToProcess.append([file, fullpath_file])

    print("<><><>to process the following files<><><>")
    print(listToProcess)

    embeddings = OpenAIEmbeddings()
    persist_directory = 'db'
    db = None


    combinedIndexExists = False
    for item in listToProcess:
        
        try:
            print("from db")
            db = FAISS.load_local(index_name, embeddings)
            combinedIndexExists = True
        except:
            print("exception occurred")
            
            #loader = TextLoader(item, encoding='utf8')
            knowledgeBase = getKnowledgeBase(item[0], root_folder, folder, embeddings)
            
            if knowledgeBase != "":
                record_doc_2_embeddings(bookeeping_dir, folder, item[1], knowledgeBase, dirnames, bookeeping_filename)
                #text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                #docs = text_splitter.split_documents(documents)

                #db = FAISS.from_documents(docs, embeddings)
                knowledgeBase.save_local(index_name)
                combined = open(bookeeping_filename,"a+")
                combined.write(item[1]+"\n")
                combined.close()
        if combinedIndexExists == True:
            knowledgeBase = getKnowledgeBase(item[0], root_folder, folder, embeddings)
            if knowledgeBase != "":
                record_doc_2_embeddings(bookeeping_dir, folder, item[1], knowledgeBase, dirnames, bookeeping_filename)
                #text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                #docs = text_splitter.split_documents(documents)

                #db = FAISS.from_documents(docs, embeddings)
                #knowledgeBase.save_local(item)
                combinedIndex = FAISS.load_local(index_name, embeddings)
                combinedIndex.merge_from(knowledgeBase)
                combinedIndex.save_local(index_name)
                combined = open(bookeeping_filename,"a+")
                combined.write(item[1]+"\n")
                combined.close()
                






#db = FAISS.load_local("index1", embeddings)
#query = "What did the president say about Ketanji Brown Jackson"
#docs = db.similarity_search(query)

#print(docs)

#query = "How much was the fee for Dhruv"
#docs = db.similarity_search(query)
#print(docs)



