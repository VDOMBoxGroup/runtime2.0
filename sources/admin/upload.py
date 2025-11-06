#from builtins import str
from uuid import uuid4
def run(request):
    sess = request.session()
    for uploaded_file in request.files.values():
        fileid = str(uuid4())
        uploaded_file.autoremove = False
        #managers.file_manager.file_upload[fileid] = attach
        sess.files[fileid] = uploaded_file
        request.write(str(fileid)+'\n')
