from blackboard_theme import blackboardScopes
from scopes import compareSelectors
import unittest

class ScopesTest(unittest.TestCase):
    def test_more_nested_scopes_have_priority(self):
        scope1 = "source.php" 
        scope2 = "source.php string.double"
        scope3 = "string.double.quoted.meta.python.huge.bloody.scope"
        
        self.assertEqual ( compareSelectors(scope1, scope2), [scope2] )
        
        self.assertEqual ( compareSelectors(scope2, scope3), [scope2] )

    def test_more_specific_scopes_have_priority(self):
        scope1 = "string.quoted.double"
        scope2 = "string"

        self.assertEqual ( compareSelectors(scope1, scope2), [scope1] )
    
    def test_should_return_both_when_selectors_are_equal(self):
        scope1 = "string.quoted"
        scope2 = "string.quoted"
        
        scope3 = "source.php string.quoted"
        scope4 = "source.python string.quoted"
                
        self.assertEqual ( compareSelectors(scope1, scope2), [scope1, scope2] )
        self.assertEqual ( compareSelectors(scope3, scope4), [scope3, scope4] )

if __name__ == "__main__":
    unittest.main()