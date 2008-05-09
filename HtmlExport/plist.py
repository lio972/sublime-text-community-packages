"""Library for Property List"""

__all__ = 'PlistError parse_plist'.split()

import sys, datetime, base64
from xml.etree import ElementTree

class PlistError(Exception):
    pass

def parse_plist(file_or_stream):
    """parse property list"""
    doc = ElementTree.parse(file_or_stream)
    root = doc.getroot()
    return plist_object(root.getchildren()[0])

def plist_object(elem):
    if elem.tag not in _HANDLERS:
        raise PlistError('%s is not supported' % elem.tag)
    else:
        return _HANDLERS[elem.tag](elem)

def plist_array(elem):
    return [plist_object(child) for child in elem.getchildren()]

def plist_data(elem):
    return  base64.b64decode(elem.text)

def plist_date(elem):
    return datetime.datetime.strptime(elem.text, '%Y-%m-%dT%H:%M:%SZ')

def plist_dict(elem):
    children = elem.getchildren()

    if len(children) % 2 != 0:
        raise PlistError('dict must have even childrens')

    dic = dict()
    for i in xrange(len(children) / 2):
        key = children[i * 2]
        value = children[i * 2 + 1]

        if key.tag != 'key': raise PlistError('key element not found')
        dic[key.text] = plist_object(value)

    return dic

def plist_real(elem):
    return float(elem.text)

def plist_integer(elem):
    return int(elem.text)

def plist_string(elem):
    return elem.text

def plist_true(elem):
    return True

def plist_false(elem):
    return False

_HANDLERS = dict((name, eval('plist_' + name))
                 for name in 'array data date dict real integer string true false'.split())

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print >>sys.stderr, 'Usage: python %s filename' % sys.argv[0]

    print parse_plist(sys.argv[1])
