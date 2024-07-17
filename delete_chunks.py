import os

from dotenv import load_dotenv
import builtins
#x=load_dotenv()

from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_structured_output_chain,
)
#from langchain.llms import OpenAI
#from langchain.embeddings import OpenAIEmbeddings
#from langchain.vectorstores import FAISS

#TEMPLATES_DIR = "templates"
#INDEX="C:\\Users\\MANISHGUPTA\\OneDrive - kyndryl\\manish\\openai\\openai-cookbook\\apps\\langchain\\index6"
#MODEL = "gpt-3.5-turbo"
#TEMP = 0.35
#embeddings = OpenAIEmbeddings()
#knowledge_base = FAISS.load_local(INDEX, embeddings)


def get_all_documents(knowledge_base):
    document_ids = []
    for doc in knowledge_base.docstore._dict:
        document_ids.append(doc)
    #print(document_ids)
    return document_ids

def get_document_ids(knowledge_base, document_pattern):
    document_ids = []
    for doc in knowledge_base.docstore._dict:
        #print(f"Content: {doc.page_content}, Metadata: {doc.metadata}")
        #if "demo-vnet" in (knowledge_base.docstore._dict[doc].metadata)['source']:
        #   print(knowledge_base.docstore._dict[doc].page_content)
        if document_pattern in str((knowledge_base.docstore._dict[doc].metadata)['source']):
            #print(knowledge_base.docstore._dict[doc].page_content)
            #print(knowledge_base.docstore._dict[doc].metadata)
            #print(doc)
            document_ids.append(doc)
        #print((knowledge_base.docstore._dict[doc].metadata)['source'])
    return document_ids

def get_document_names(knowledge_base):
    document_names = []
    for doc in knowledge_base.docstore._dict:
        document_names.append(str((knowledge_base.docstore._dict[doc].metadata)['source']))
    return document_names

#import faiss

def delete_document(knowledge_base, document_pattern, index_path):
    document_ids = get_document_ids(knowledge_base, document_pattern)
    print(document_ids)
    try:
        #print("Here xyz")
        #print(document_ids[0])
        #print("Here xyza")
        #print(knowledge_base.docstore.search(document_ids[0]))
        #print("Here pppp")
        #exit()
        knowledge_base.delete(document_ids)
        #knowledge_base.save_local(index_name)
        knowledge_base.save_local(index_path)
        #faiss.write_index(knowledge_base.index, index_path)
    except:
        pass
    
    print("documents deleted: ", document_ids)      


#document_pattern = "files6/US20220405481.txt"

#print(len(get_all_documents(knowledge_base)))
#delete_document(knowledge_base, document_pattern, INDEX)
#print(len(get_all_documents(knowledge_base)))

