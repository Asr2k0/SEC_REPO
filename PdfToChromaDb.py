"""

This script has been exclusively created to chunk the PDFS and store them  in Chroma DB .


"""




import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document

from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Function to load all PDFs from a directory
def load_pdfs_from_directory(filing_dir="filings"):
    """
    This function scans a specified directory for subfolders and gathers all PDF file paths within each subfolder.
     Each subfolder represents a separate entity (like a company),
      making it easy to organize PDFs by category. The function returns a list of paths to all detected PDF files.

    :param filing_dir: directory where the SEC filings are stored
    :return: list of pdf_docs
    """
    try :
        pdf_docs = []
        for ticker_folder in os.listdir(filing_dir):
            ticker_folder_path = os.path.join(filing_dir, ticker_folder)
            if os.path.isdir(ticker_folder_path):
                for file_name in os.listdir(ticker_folder_path):
                    if file_name.endswith(".pdf"):
                        pdf_path = os.path.join(ticker_folder_path, file_name)
                        pdf_docs.append(pdf_path)
        return pdf_docs
    except:
        print(f'Error occured in {load_pdfs_from_directory}')


# Function to extract text from PDFs
def get_pdf_text(pdf_paths):
    """
    This function reads the text content of each PDF in a given list of file paths. It uses the PyPDFLoader to split the PDF pages,
     extracting the text page-by-page. If an error occurs while processing a PDF, it logs the error and continues.

    :param pdf_paths:paths to pdf
    :return: the text for each pdf
    """
    text = ""
    for pdf in pdf_paths:
        try:
            loader = PyPDFLoader(pdf)
            pages = loader.load_and_split()
            for page in pages:
                text += page.page_content
        except Exception as e:
            print(f"Error extracting text from {pdf}: {e}")
    return text


# Function to split text into chunks
def get_text_chunks(text):
    """
    This function splits large text into smaller chunks using a recursive character-based method,
     with each chunk having an overlap to maintain context. It defines the size and overlap for each chunk, ensuring that the continuity
     of information is preserved across boundaries. The function returns a list of text chunks, ready for further processing.
    :param text: Text of documents
    :return: list of text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,  # Size of each chunk
        chunk_overlap=200,  # Overlap between chunks to ensure continuity
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks


# Function to extract metadata from the PDF filename (automatically)
def extract_metadata_from_filename(pdf_path):
    """
    This function extracts metadata (company name, form type, year, quarter) from the PDF file name based on specific naming conventions.
     It splits the file name and deduces quarter information depending on the form type.
    The metadata is returned as a dictionary for easy association with each document chunk.

    :param pdf_path:
    :return:
    """
    filename = os.path.basename(pdf_path)

    # Regex to extract company_name, form_type, year, and quarter from the filename
    path_list = filename.split('_')
    if len(path_list) == 3:
        company = path_list[0]
        type = path_list[1]
        year = path_list[2].split('.')[0]
        quarter = 'Q4' if type == '10K' else 'Q1'  # Default to Q4 for 10-K forms, Q1 for 10-Q
    else:
        company = path_list[0]
        type = path_list[1]
        year = path_list[2].split('.')[0]
        quarter = path_list[3].split('.')[0]

    return {
        "company_name": company,
        "form_type": type,
        "year": year,
        "quarter": quarter
    }


# Function to create a vector store using Chroma from documents
def create_vectorstore_from_documents(pdf_paths):
    """
    This function prepares documents by extracting text, splitting it into chunks, and adding metadata. Each chunked text section is wrapped in a
     Document object that contains the associated metadata. The function returns a list of document objects ready for embedding.

    :param pdf_paths:
    :return:
    """
    documents = []

    for pdf_path in pdf_paths:
        # Extract text from PDF
        text = get_pdf_text([pdf_path])

        # Split text into chunks
        text_chunks = get_text_chunks(text)

        # Automatically generate metadata from the filename
        metadata = extract_metadata_from_filename(pdf_path)

        if metadata:  # Only proceed if metadata extraction is successful
            # Create Document objects with the extracted metadata
            for chunk in text_chunks:
                doc = Document(
                    page_content=chunk,
                    metadata=metadata
                )
                documents.append(doc)

    return documents


# Store the vectorstore in ChromaDB
def store_in_chromadb_in_batches(documents, batch_size=5461, persist_dir='./chroma_db'):
    """

    his function stores the document list in ChromaDB, processing the list in batches to manage memory usage efficiently.
     It initializes embeddings using OpenAIEmbeddings, divides documents into batches, and saves each batch in a persistent vector store.
     Once completed, it prints a confirmation message indicating successful storage.

    """
    embeddings = OpenAIEmbeddings()  # Initialize embeddings
    # Process documents in batches
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]  # Get the batch of documents
        # Create the vector store from the batch of documents
        Chroma.from_documents(batch, embeddings, persist_directory=persist_dir)

    print("Vector store created and stored in ChromaDB in batches.")


if __name__ == "__main__":
    filing_dir = "./Data/filings/"
    pdf_paths = load_pdfs_from_directory(filing_dir)
    print(pdf_paths)

    if pdf_paths:
        print(f"Loaded {len(pdf_paths)} PDFs: {pdf_paths}")


        documents = create_vectorstore_from_documents(pdf_paths)


        store_in_chromadb_in_batches(documents)

    else:
        print("No PDFs found in the directory.")
