import re

SECTION_PATTERN = r"\n\d+\.?\s+[A-Z][A-Za-z ]+\n"

def section_split(text):
  parts = re.split(SECTION_PATTERN,text)
  labels = re.findall(SECTION_PATTERN,text)
  
  sections = []
  
  for i,part in enumerate(parts):
    if i == 0:
      sections.append({
        "title": "Abstract",
        "text": part.strip()
      })
      continue
    sections.append({
        "title": labels[i-1].strip(),
        "text": part.strip()
      })
    
  return sections

def chunk_text(text,max_words = 300):
  sections = section_split(text)
  all_chunks = []
  
  for section in sections:
    texts = section["text"].replace("\r\n", "\n")
    paras = re.split(r"\n\n\s{2,}|\s{2,}|\n\s{2,}", texts)
    para = [p.strip() for p in paras if p.strip()]
    
    current  = []
    word_count = 0
    
    for p in para:
      w = len(p)
      
      if word_count + w > max_words and current:
        all_chunks.append({
          "section": section["title"],
          "text": "\n\n".join(current)
        })
        
        current = []
        word_count = 0
      
      current.append(p)
      word_count += w
    if current:
      all_chunks.append({
          "section": section["title"],
          "text": "\n\n".join(current)
        })
  
  print(f"No. of chunks {len(all_chunks)}")
  return all_chunks