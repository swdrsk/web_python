#coding:utf-8


def conv_encoding(data):
    lookup = ['utf_8','utf-8', 'euc_jp','cp932', 'euc_jis_2004', 'euc_jisx0213',
              'shift_jis', 'shift_jis_2004','shift_jisx0213',
              'iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3',
              'iso2022_jp_ext','latin_1', 'ascii']
    encode = None
    for encoding in lookup:
        try:
            data = data.decode(encoding)
            encode = encoding
            break
        except:
            pass
    if isinstance(data, unicode):
        return data,encode
    else:
        raise LookupError

    
def find_ja(data):
    rst = False
    try:
        data = data.encode('utf-8')
    except:
        data = data.encode('cp932')
    return rst
