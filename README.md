# DGFISMA_pdf_processing


use "dbuild.sh" to build the docker image 

use "dcli.sh" to start a docker container

Given a document (json), the app will return a json with one key: "text."

The to be POSTed json should contain the following fields:
"path_to_pdf" - specifying where the PDF is stored
"source" - specifying whether the PDF is an EurLex Regulation/Directive or other. 

The processing pipeline will be chosen accordingly. 
The current version of the app doesn't use BERT.  
