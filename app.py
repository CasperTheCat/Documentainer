from flask import Flask, escape, request, send_file, Response
from shutil import copyfileobj
from io import StringIO, BytesIO
import pypandoc
app = Flask(__name__)

#methods = ['POST']

supportedToTypes = ["Latex", "Markdown", "HTML"]
supportedFromTypes = supportedToTypes # Redundant

typeTranslation = {
    'Latex': 'tex',
    'Markdown': 'md',
    'HTML': 'html'
}

def GenerateResponse(text: str, status: int = 200):
    return Response(text, status=status)

def GenerateStatus(status: int = 200):
    return GenerateResponse('', status=status)

def CheckSupport(toLang: str, fromLang: str) -> bool:
    return toLang in supportedToTypes and fromLang in supportedFromTypes


def Convert(toLang: str, fromLang: str, data: str, useStandalone: bool):
    args = []

    if useStandalone:
        args.append('-s')


    odata = pypandoc.convert_text(data, typeTranslation[toLang], format=typeTranslation[fromLang], extra_args=args)
    return BytesIO(odata.encode()), '.' + typeTranslation[toLang]

@app.route('/', methods = ['GET', 'POST'])
def main():
    # Args
    toLang = request.args.get("to", "Latex")
    fromLang = request.args.get("from", "Markdown")
    standalone = request.args.get("standalone","DEFAULT")

    # Flags
    bUseStandalone = (not standalone == "DEFAULT")

    #print('{} {}'.format(toLang, fromLang))
    IsSupported = CheckSupport(toLang, fromLang)

    if request.method == 'GET':
        return GenerateStatus() if IsSupported else GenerateStatus(405)
    elif request.method == 'POST':
        if IsSupported:
            try:
                #reqData = request.get_json(silent=True)
                reqData = request.data
                output, extension = Convert(toLang, fromLang, reqData, bUseStandalone)
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