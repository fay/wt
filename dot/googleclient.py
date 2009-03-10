from GoogleReader import GoogleReader
def get_reader():
    reader = GoogleReader()
    reader.identify('tzf1943@21cn.com', '02515633tzf')
    reader.login()
    return reader