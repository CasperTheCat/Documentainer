from flask import Flask, escape, request, send_file, Response
from shutil import copyfileobj
from io import StringIO, BytesIO
import pypandoc
app = Flask(__name__)

#methods = ['POST']

supportedToTypes = ["Latex", "Markdown"]
supportedFromTypes = supportedToTypes # Redundant

typeTranslation = {
    'Latex': 'tex',
    'Markdown': 'md'
}

def GenerateResponse(text: str, status: int = 200):
    return Response(text, status=status)

def GenerateStatus(status: int = 200):
    return GenerateResponse('', status=status)

def CheckSupport(toLang: str, fromLang: str) -> bool:
    return toLang in supportedToTypes and fromLang in supportedFromTypes


def Convert(toLang: str, fromLang: str, data: str):
    odata = pypandoc.convert_text(data, typeTranslation[toLang], format=typeTranslation[fromLang], extra_args=['-s'])
    return BytesIO(odata.encode()), '.' + typeTranslation[toLang]

@app.route('/', methods = ['GET', 'POST'])
def main():
    toLang = request.args.get("to", "Latex")
    fromLang = request.args.get("from", "Markdown")

    #print('{} {}'.format(toLang, fromLang))
    IsSupported = CheckSupport(toLang, fromLang)

    if request.method == 'GET':
        return GenerateStatus() if IsSupported else GenerateStatus(405)
    elif request.method == 'POST':
        if IsSupported:
            try:
                #reqData = request.get_json(silent=True)
                reqData = request.data
                output, extension = Convert(toLang, fromLang, reqData)
                response = send_file(output, as_attachment=True, attachment_filename='download' + extension)
                return response
            except Exception as e:
                # Something died!
                if app.debug:
                    return GenerateResponse(repr(e), 400)
                else:
                    return GenerateStatus(400) # Maybe there is a better way
        else:
            return GenerateStatus(405)

    return GenerateStatus(500)