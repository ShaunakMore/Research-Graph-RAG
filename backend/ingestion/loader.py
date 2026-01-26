import pypdf as pdf

def load_pdf(pdf_stream):
  pdf_reader = pdf.PdfReader(pdf_stream)
  text = ""
  
  for i,page in enumerate(pdf_reader.pages):
    if page:
      text += f" === PAGE {i+1} === \n"
      text+=page.extract_text()
    
  return text.strip()
  
text = load_pdf("./data/bert.pdf")