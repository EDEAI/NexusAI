from file_utils import fix_url

def test_fix_url():
    patterns = [
        ("/files/test.txt", "https://example.net", "https://example.net/files/test.txt"),
        ("/files/test.txt", "https://example.net/", "https://example.net/files/test.txt"),
        ("/test.txt", "https://example.net/", "/test.txt"),
        ("https://example.com/files/test.txt", "https://example.net", "https://example.net/files/test.txt"),
        ("https://example.com/files/test.txt", "https://example.net/", "https://example.net/files/test.txt"),
        ("https://example.com/test.txt", "https://example.net/", "https://example.com/test.txt"),
    ]
    for old_url, new_base_url, expected in patterns:
        assert fix_url(old_url, new_base_url) == expected
