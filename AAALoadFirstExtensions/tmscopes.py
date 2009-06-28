#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs

# Sublime Imports
import sublime
import sublimeplugin

#################################### README ####################################
"""

Horrible, horrible implementation of sorting, by scoping bestmatch

"""
################################################################################

def memoize(func):
    saved = {}
    def call(*args):
        try:
            return saved[args]
        except KeyError:
            res = func(*args)
            saved[args] = res
            return res
        except TypeError:
            # Unhashable argument
            return func(*args)
    call.func_name = func.func_name
    return call

def normalize_scope(scope):
    """ Sublime returns scopes that are not sane!

        >>> for pt in xrange(0, view.size()):
        >>>     scope = view.syntaxName(pt)
        >>>     assert view.matchSelector(pt, normalize_scope(scope))

    """

    return ' '.join(reversed(map(unicode.strip, scope.split())))

def leveled_scopes(scope):
    # TODO:

    scope = ' '.join(scope.split(' -')[:1])  #   ignore - operator
    scope = ' '.join(scope.split( '|')[:1])  #   ignore || operators

    scope = [l.strip() for l in scope.split(' ')]
    return [['python' if s =='py' else s for s in l.split('.')] for l in scope]

def filter_last(specificity):
    specificity = specificity[:]

    while specificity and specificity[-1] is None:
        specificity.pop()

    return specificity

@memoize
def selector_specificity(selector, scope):
    allSelectors, allScopes = map(leveled_scopes, (selector, scope))

    level = -1
    specificity = [None] * len(allSelectors)

    for i, selectors in enumerate(allSelectors):
        for element_depth, scopes in enumerate(allScopes[level+1:]):
            # all selectors match
            if not [s for s in selectors if s not in scopes]:
                specificity[i] = (element_depth+1,  len(selectors))
                level = element_depth

        if not specificity[i]: return []

    return specificity

def compare_candidates(c1, c2):
    either_is_greater = cmp(len(c1), len(c2))
    if either_is_greater: return either_is_greater

    cd1, cd2 = c1[:], c2[:]

    while cd1 and cd2:
        either_is_greater = cmp(cd1.pop(), cd2.pop())
        if either_is_greater: return either_is_greater

    return cmp(cd1, cd2)

def sort_candidates(candidates):
    return sorted (
        candidates,
        cmp=compare_candidates,
        key= lambda i: i[0],
        reverse=True )

def sort_by_scope(view, to_sort, scope_index=0):
    pt = view.sel()[0].begin()
    scope_at_point = normalize_scope(view.syntaxName(pt))

    candidates =[]

    for i, item in enumerate(to_sort):
        selectors = item[scope_index].split(',')

        for selector in selectors:
            if view.matchSelector(pt, selector):
                specificity = selector_specificity(selector, scope_at_point)
                if specificity:
                    candidates.append((specificity, i ))

    if candidates:
        sorted_candiates = sort_candidates(candidates)
        candidates = []

        for c in sorted_candiates:
            # sorted best to worst match
            # multiple `selectors` per list item index
            # so take best
            if c not in candidates:
                candidates.append(c[1])

        # Put the rest in there
        # TODO:  if keep_non_matches: yada yada
        candidates.extend([ i for i in range(len(to_sort)) if
                              not i in candidates ])

        return [to_sort[i] for i in candidates]
    else:
        return to_sort

################################################################################