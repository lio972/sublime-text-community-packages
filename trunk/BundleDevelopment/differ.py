################################################################################

import difflib

a = (
"""def junk(jonny, rotten):
    pass
    """
)

b = (
"""def monk hinh():
    nothing
    """
)

s = difflib.SequenceMatcher(a=a, b=b)

def is_noise(chunk):
    return len(chunk) < 3 and chunk.isalpha()

similar = []
for a_start, b_start, length in s.get_matching_blocks():
    chunk = a[a_start:a_start+length]
    if length and not is_noise(chunk):
        similar += [chunk]

snippet = []
for i, chunk in enumerate(similar):
    if i > 0:
        snippet += ['${%s:tabstop}' % i]
    snippet += [chunk]

print ''.join(snippet)

################################################################################