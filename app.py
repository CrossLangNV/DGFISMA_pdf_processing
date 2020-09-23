from flask import Flask
from flask import request
from flask import abort
import process_eurlex_regex
import process_plain_pdf

app = Flask(__name__)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    if not request.json:
        abort(400) 
    if ('source' not in request.json):
        print( "'source' field missing" )
    else:
        if request.json['source'] == 'eurlex_directive' or request.json['source'] == 'eurlex_regulation':
            try:
                text = pdf_pipeline_regex.extract_text(request.json['path_to_pdf'])
            except:
                text = process_plain_pdf.extract_text(request.json['path_to_pdf'])
        if request.json['source'] != 'eurlex_directive' or request.json['source'] != 'eurlex_regulation':
            text = process_plain_pdf.extract_text(request.json['path_to_pdf'])
    return {"text" : text}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)