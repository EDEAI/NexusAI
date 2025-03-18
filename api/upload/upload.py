from datetime import date
from mimetypes import guess_type
from fastapi import APIRouter, File
from core.database.models import (
    UploadFiles,
)
from api.utils.common import *
from api.utils.jwt import *
from api.schema.vector import *
from languages import get_language_content

router = APIRouter()


@router.post('/upload_file', response_model=UploadFileResponse)
async def upload_file(file: UploadFile = File(...), userinfo: TokenData = Depends(get_current_user)) -> UploadFileResponse:
    """
    Upload file to the server

    constraint
        Support TXT, MARKDOWN, PDF, HTML, XLSX, XLS, DOCX, CSV, each file does not exceed 15MB

    Returns:
        The ID of the newly created file.
    """
    extensions_all = {'.txt', '.md', '.pdf', '.html', '.xlsx', '.xls', '.docx', '.csv', '.png', '.jpg', '.jpeg'}
    max_file_size = 15 * 1024 * 1024
    user_id = userinfo.uid
    filename = file.filename
    content_type = file.content_type
    if content_type is None:
        content_type = guess_type(file.filename)[0]

    file_extension = Path(filename).suffix

    if file_extension not in extensions_all:
        return response_error(get_language_content("api_upload_unsupported"))

    if file.size > max_file_size:
        return response_error(get_language_content("api_upload_max_size"))

    today = date.today()
    today_path = project_root.joinpath(
        'upload_files',
        str(today.year),
        str(today.month),
        str(today.day)
    )
    today_path.mkdir(parents=True, exist_ok=True)
    original_file_path = today_path.joinpath(filename)
    new_file_path = original_file_path.with_stem(uuid4().hex)
    with new_file_path.open('wb') as file_io:
        while content := await file.read(1_048_576):
            file_io.write(content)
    row = {
        'user_id': user_id,
        'name': original_file_path.stem,
        'path': str(new_file_path.relative_to(project_root)).replace("\\", "/"),
        'size': file.size,
        'extension': original_file_path.suffix,
        'mime_type': content_type
    }
    file_id = UploadFiles().insert(row)
    row['file_id'] = file_id
    return response_success(row, get_language_content("api_vector_success"))