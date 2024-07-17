import yaml
from pathlib import Path
from typing import Union, Optional, List

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

class YAMLLoader(BaseLoader):
    def __init__(
        self,
        file_path: Union[str, Path],
        content_key: Optional[str] = None,
        ):
        self.file_path = Path(file_path).resolve()
        self._content_key = content_key
    

    
    def create_documents(self, processed_data):
        documents = []
        content = processed_data
        document = Document(page_content=content, metadata={"source": self.file_path})
        documents.append(document)
        return documents
    

    

    def load(self) -> List[Document]:
        """Load and return documents from the JSON file."""

        docs=[]
        with open(self.file_path, 'r') as normal_file:
            data = normal_file.read()
            docs = self.create_documents(data)
 
        return docs
    
#filepath = "files4/example1.yaml"
#tempfilepath = "files4/temp.json"


#loader = YAMLLoader(filepath)

#print(loader.load())
