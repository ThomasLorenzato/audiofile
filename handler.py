from flask import Response
import io
from PIL import Image
from requests_toolbelt.multipart import decoder

def handle(event, context):
    '''
    expected event headers
    imageType: type of sent image
    convertType: image type to output
    expected in event body
    imageData: raw data of the image
    '''
    if not event.body:
        return Response(
            '{"error" : "No image data"}',
            status = 400,
            content_type = "application/json"
        )


    convertType = event.headers.get("convertType").lower()

    multipart_data = decoder.MultipartDecoder(event.body, event.headers.get("Content-Type"))

    imageData = None

    for part in multipart_data.parts:
        if b'filename=' in part.headers.get(b'Content-Disposition', b""):
            imageData = part.content
            break

    ## open the image as a buffer and save to output buffer
    inputImage = Image.open(io.BytesIO(imageData))

    outputBuffer = io.BytesIO()
    inputImage.save(outputBuffer, format=convertType.upper())

    outputBuffer.seek(0)

    def generate():
       while chunk := outputBuffer.read(4096):
           yield chunk

    contentType = f"image/{convertType}"

    return Response(
            generate(),
            status=200,
            content_type=contentType,
            headers={
                "Content-Disposition": "attachment; filename=converted." + convertType,
                "Accept-Ranges": "bytes",
                "Cache-Control": "no-cache"
            }
    )
