# coding=utf-8
import pdftotext
import re
import sys
import string


def concatenate_segments(text_as_list):
    '''
    since legal documents always respect proper punctuation we can rely on it
    to decide whether the line should be followed by a break, or it continues
    '''

    clean_text = []
    for line in text_as_list:
        if len(line) > 1:  # don't process empty newlines
            if line[-1] in string.punctuation.replace(',', '') or ('Article' in line and line[-1].isdigit()):
                line = line.strip() + '\n'
                clean_text.append(line)
            else:
                clean_text.append(line.strip() + ' ')

    return clean_text


def rearrange_text(page):
    """
    :param page: columned or continuous text as a string
    :return: text in the right order, also as a string

    Since pdftotext preserves the layout of the original pdf,
      we iterate over each row of the page to:
       1. determine the most common length of each row
       2. determine whether the text is continuous or columned

    If the pattern, i.e. multiple consequent empty spaces,
      is not found in the first third of most rows,
      we assume that the text is columned.

    We iterate over the text once again to split each row into segments of column 1 and 2.

    When the columns are concatenated in the right order, the only thing left is to determine
    which consequent elements belong to the same sentence and which ones don't.
    """
    last_page_of_the_doc = False
    page = page.split('ANNEX', 1)[0]  # if page doesn't have an annex it won't change
    if 'This Regulation shall be binding' in page:
        signature = 'This Regulation shall be binding' + page.split('This Regulation shall be binding')[1]
        page = page.split('This Regulation shall be binding')[0]
        last_page_of_the_doc = True

    text_as_list = page.split('\n')
    list_of_breaks = []
    lengths = []
    for l in text_as_list:  # looking for all lengths and line breaks
        pattern = r'\s\s\s\s+'
        list_of_breaks.append([m.end(0) for m in re.finditer(pattern, l)])
        lengths.append(len(l))

    list_of_breaks = list(filter(None, list_of_breaks))

    split_page_at = max(list_of_breaks, key=list_of_breaks.count)
    split_page_at = split_page_at[0]  # sometimes an array is returned by re.finditer but we only need the first match
    one_third_of_line = max(lengths) / 3
    if split_page_at > one_third_of_line:  # most of the text is divided into columns
        col1 = []
        col2 = []
        for line in text_as_list:
            c1 = line[:split_page_at - 1]
            c2 = line[split_page_at:]
            col1.append(c1)
            col2.append(c2)
        clean_page = col1 + col2
        # clean_text = concatenate_segments(clean_page)

    else:  # the text is continuous
        # clean_text = concatenate_segments(text_as_list)
        clean_page = text_as_list

    # making sure we don't lose any info
    if last_page_of_the_doc:
        clean_signature = []
        for x in signature.split('\n'):
            clean_signature.append(x.strip())
        clean_text = concatenate_segments(clean_page + clean_signature)
    else:
        clean_text = concatenate_segments(clean_page)

    # trying to get rid of noisy footnotes. doesn't always work
    for x in clean_text:
        if 'OJ ' in x or 'OT ' in x or ' of this Official Journal ' in x or '         Official Journal of the' in x:
            clean_text.remove(x)

    clean_page = ''.join(clean_text)
    return clean_page


def get_head(page):
    """
    This function only works for EurLex documents, since the layout is uniform.
    It takes the first page as a string and returns two strings: the head and the rest of the body
    """

    page = page.split('THE', 1)
    head = []
    for x in page[0].split('\n')[1:]:
        head.append(x.strip())
    head = ' '.join(head)
    body = 'THE' + page[1]
    return head, body


def preprocess_pages(pdfObject):
    pdfList = list(pdfObject)  # transforming the object into a list to iterate over pages
    if len(pdfList) > 1:
        head, first_page = get_head(pdfList[0])  # the first page is being processed separately
        first_page = rearrange_text(first_page)
        pages = [first_page]
        for page in pdfList[1:]:  # process the rest of the pdf
            page = '\n'.join(page.split('\n')[1:])
            arranged_page = rearrange_text(page)
            pages.append(arranged_page)

        page = '\n'.join(pages)

    else:
        page = ''.join(pdfList)
        head, body = get_head(page)
        page = rearrange_text(body)

    clean_page = []

    # cleaning the heading from abundant spaces
    for line in head.split('\n'):
        line = line.strip() + '\n'
        clean_page.append(line)

    # cleaning the body from hyphens
    for line in page.split('\n'):
        line = line.strip().replace('\xad ', '').replace('\xad', '')
        if len(line) == 0:
            line = '\n'
        clean_page.append(line + ' ')
    clean_page = '\n'.join(clean_page)
    return clean_page

def extract_text(path_to_pdf):
    pdfFileObj = open(path_to_pdf, 'rb')
    pdf = pdftotext.PDF(pdfFileObj)
    text = preprocess_pages(pdf)
    return text
