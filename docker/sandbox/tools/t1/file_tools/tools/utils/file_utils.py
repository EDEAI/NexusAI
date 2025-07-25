def fix_file_url(file: dict, files_url: str) -> dict:
    if hasattr(file, 'url') and isinstance(file.url, str):
        file.url = fix_url(file.url, files_url)
    return file

def fix_url(old_url: str, files_url: str) -> str:
    files_url = files_url.rstrip('/')
    idx = old_url.find('/files')
    if idx != -1:
        return files_url + old_url[idx:]
    else:
        return old_url
