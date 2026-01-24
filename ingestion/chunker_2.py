from langchain.document_loaders import PyPDFLoader
import pprint
pdf_loader = PyPDFLoader("./data/bert.pdf")

pages = pdf_loader.load()

pprint.pp(pages[0].metadata)