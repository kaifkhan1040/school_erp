from django.core.exceptions import ValidationError
from django.conf import settings
import magic
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile



def file_extension_validator(value):
    valid_extensions_file = ('pdf', 'png', 'jpeg', 'jpg')
    try:
        if value:
            file_name = value.name
            file_extension = file_name.split('.')[-1].lower()
            if file_extension in valid_extensions_file:
                if value.size > int(settings.MAX_UPLOAD_SIZE):
                    raise ValidationError("Please keep the file size under 100 MB")
            else:
                raise ValidationError("Please upload file in PDF/PNG/JPG/JPEG formats.")
    except Exception:
        return True


def image_extension_validator(value):
    valid_extensions_image = ('png', 'jpeg', 'jpg', 'pdf')
    try:
        if value:
            image_name = value.name
            image_file_extension = image_name.split('.')[-1].lower()
            if image_file_extension in valid_extensions_image:
                if value.size > int(settings.MAX_UPLOAD_SIZE):
                    raise ValidationError({"detail": "Please keep the file size under 10 MB"})
            else:
                raise ValidationError({"detail": "Please upload image in PDF/PNG/JPG/JPEG formats."})
    except Exception:
        return True

def validate_video(value):
    # Ensure the uploaded file is a video
    if isinstance(value, UploadedFile):
        # Use python-magic to detect the MIME type of the file
        mime = magic.from_buffer(value.read(1024), mime=True)
        if mime.split('/')[0] != 'video':
            raise ValidationError("Only video files are allowed.")

    # You can also validate the file extension if necessary
    # if not value.name.endswith('.mp4'):
    #     raise ValidationError("Only MP4 video files are allowed.")
