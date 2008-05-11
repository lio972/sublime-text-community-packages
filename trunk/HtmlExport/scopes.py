def nesting(scope):
    return len(scope.split(' '))

def last_nested(scope):
    return len(scope.split(' ')[-1].strip().split('.'))

def compareSelectors(scope1, scope2):
    nesting1, nesting2 = map(nesting, (scope1, scope2))
    
    if nesting1 > nesting2: return [scope1]
    elif nesting2 > nesting1: return [scope2]
    
    else:
        last_sel1, last_sel2 = map(last_nested, (scope1, scope2))
        
        if last_sel1 > last_sel2: return [scope1]
        elif last_sel2 > last_sel1: return [scope2]
        else: return [scope1, scope2]
        
        
class Selector(object):
    def __init__(self, scope):
        self.scope = scope
    
    def __eq__(self, other):
        return len(compareSelectors(self.scope, other.scope)) == 2
    
    def __ne__(self, other):
        return not (self == other)
    
    def __lt__(self, other):
        return compareSelectors(self.scope, other.scope) == [other.scope]
    
    def __lte__(self, other):
        return self < other or self == other
    
    def __gt__(self, other):
        return not self < other
    
    def __gte__(self, other):
        return self > other or self == other
    
    def __str__(self):
        return self.scope
    
    def __unicode__(self):
        return self.scope
        

if __name__ == "__main__":
    assert Selector('source.php') == Selector('source.python')
    
    assert Selector('source.php') < Selector('source.php string')
    
    assert Selector('source.python') != Selector('source.python.monkey')
    
    assert Selector('source.python') <= Selector('source.python.monkey')