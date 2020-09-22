# coding=utf-8
import pdftotext
import re
import sys
import torch
from torch.nn.functional import softmax
from transformers import BertForNextSentencePrediction, BertTokenizer


def apply_bert(text):
    model = BertForNextSentencePrediction.from_pretrained(sys.argv[2])
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    output = []
    for i, seq_A in enumerate(text[:-1]):
        seq_B = text[i + 1]
        encoded = tokenizer.encode_plus(seq_A, text_pair=seq_B, return_tensors='pt')
        seq_relationship_logits = model(**encoded)[0]
        probs = softmax(seq_relationship_logits, dim=1)
        if probs.data[0][0] > 0.6:
            output.append(seq_A.replace('\n', '') + ' ')
        else:
            output.append(seq_A)
    output.append(text[-1])
    return ''.join(output)

def rearrange_text(page):
    page = page.split('ANNEX', 1)[0]
    if 'This Regulation shall be binding' in page:
       page = page.split('This Regulation shall be binding')[0]
    text_as_list = page.split('\n')
    list_of_breaks = []
    lengths = []
    for l in text_as_list:
        pattern = r'\s\s\s\s+'
        list_of_breaks.append([m.end(0) for m in re.finditer(pattern, l)])
        lengths.append(len(l))
    list_of_breaks = list(filter(None, list_of_breaks))
    split_page_at = max(list_of_breaks, key=list_of_breaks.count)  # get the middle of the page
    split_page_at = split_page_at[0]
    if split_page_at > max(lengths) / 3:  # checking if the pdf is divided in columns
        col1 = []
        col2 = []
        for line in text_as_list:
            c1 = line[:split_page_at - 1]
            c2 = line[split_page_at:]
            
            # getting rid of footnotes
            
            if not 'OJ ' in c1 or 'OT ' in c1 or ' of this Official Journal ' in c1 or '         Official Journal of the' in c1:
                col1.append(c1)
            if not 'OJ ' in c2 or 'OT ' in c2 or ' of this Official Journal ' in c2 or '         Official Journal of the' in c2:
                col2.append(c2)

        clean_page = col1 + col2
        clean_page = '\n'.join(clean_page)
    else:
        clean_text = []
        for line in text_as_list:
            if len(line) > 1:
                if not 'OJ ' in line or 'OT ' in line or ' of this Official Journal ' in line or '         Official Journal of the' in line:  # doesn't work too well for footnotes with multiple lines
                    clean_text.append(line + '\n')
        clean_page = '\n'.join(clean_text)

    return clean_page


def get_head(page):
    page = page.split('THE', 1)
    head = []
    for x in page[0].split('\n')[1:]:
        head.append(x.strip())
    head = ' '.join(head)
    body = 'THE' + page[1]
    return head, body


def preprocess_pages(pdfObject):
    pdfList = list(pdfObject)
    if len(pdfList) > 1:
        head, first_page = get_head(pdfList[0])
        first_page = rearrange_text(first_page)
        pages = [first_page]
        for page in pdfList[1:]:
            page = '\n'.join(page.split('\n')[1:])
            arranged_page = rearrange_text(page)
            pages.append(arranged_page)
        page = '\n'.join(pages)
    else:
        page = ''.join(pdfList)
        head, body = get_head(page)
        page = rearrange_text(body)

    clean_page = []
    for line in head.split('\n'):
        line = line.strip() + '\n'
        clean_page.append(line)
    for line in page.split('\n'):
        line = line.strip().replace('\xad', '')
        if len(line) == 0:
            line = '\n'
        clean_page.append(line + ' ')
    return clean_page  # text as a list


if __name__ == "__main__":
    pdfFileObj = open(sys.argv[1], 'rb')
    pdf = pdftotext.PDF(pdfFileObj)
    page = preprocess_pages(pdf)
    clean_page = apply_bert(page)
    print(clean_page)
