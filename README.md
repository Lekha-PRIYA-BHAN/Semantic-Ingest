# Repository: ingest

**Here is the github repo that will ingest data into a vector database (****FAISS****). The documents will be chunkified and then the embeddings for the chunks are persisted locally in the root folder where the program in this repository is run. Right now OpenAI is used to obtain embeddings but we can replace this with a free LLM.**

# Prerequisites

**Python Version**:

Ensure that the version of python should be >= 3.11.0

Run the following command to check what version you have.

```
python --version
```

**OpenAI key**:

Obtain an OpenAI key

# Get ready to ingest documents to Vector Database

Open a command prompt on Windows 10 (commands on Linux will be similar :-)

Run the following commands in the following order:

* `1. setup-env.bat`
* `2. prepare-env.bat`

If the above commands are executed without problems then you are ready to ingest and index documents.

To ingest documents of your choice do the following:

**Step 1**: Create a file named "`.env`" in the root folder, and put your OpenAI or Azure OpenAI credentials. Look at the file env.txt to see an example of AzureOpenAI. If you want to use OpenAI instead then comment out the parameter `OPENAI_DEPLOYMENT_NAME` and supply the value for the parameter `OPENAI_API_KEY`

for example:

`OPENAI_API_KEY=sk-aQqHVSapwl9J4bz5O2p3T3Blbk4JI3AUNeUOQVPOM5Uv2Tlr`

For Azure OpenAI supply the parameters:

```
OPENAI_API_TYPE= "azure"
OPENAI_API_VERSION = "2023-05-15"
OPENAI_API_BASE = "https://aoi-mg.openai.azure.com/openai"
OPENAI_API_KEY = "7f50bff8153f48363d76"
OPENAI_DEPLOYMENT_NAME="mg-embedding"
OPENAI_MODEL_NAME="text-embedding-ada-002"
```

To point to a directory containing the files to be indexed specify the following triple in the `.env`:

```
ROOT_PATH="C:/Users/MANISHGUPTA/OneDrive - kyndryl/manish/openai/openai-cookbook/apps/langchain"
INDEX_NAME="<give a representative name to the index, e.g. index1>"
FOLDER_TO_INDEX="<name of the directory (e.g. files1) under ROOT_PATH that will contain the files to be indexed>"
```

**Step 2**: In the folder "`FOLDER_TO_INDEX`" put your documents in ".pdf" or ".txt" or ".docx" or ".md" extensions. Yes you can have a hierarchical folder structure under the "`FOLDER_TO_INDEX`" folder.

For the starters we have put a file named "`state_of_the_union.txt`" under `files1` which you can remove if you like. 

**Step 3**: within the python virtual environment created earlier execute the following command:
`python create_index_v3.py`

If `INDEX_NAME` was equal to `index1` then this will result in creation of an index called "`index1`" under the root folder. This index can be used to query using NLP.
