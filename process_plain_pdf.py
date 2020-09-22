import fitz

def extract_text(path_to_pdf):
    doc = fitz.open(path_to_pdf)
    text = []
    for page in doc:
        blocks = page.getText("blocks")  # blocks is a list of tuples
        for b in blocks:
            text.append(b[-3])  # selecting text
    text = '\n'.join(text)
    return text