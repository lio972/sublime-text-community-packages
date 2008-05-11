import build_css, unittest

from blackboard_theme import blackBoard

class TestCssBuilder(unittest.TestCase):
    def test_inane(self):
        self.assertEqual(blackBoard['author'], "Domenico Carbotta")
    
    def test_createTitle(self):
        self.assertEqual( build_css.createTitle(blackBoard),
            "Theme: Blackboard\nAuthor: Domenico Carbotta",
        )
    
    def test_createMainRule(self):
        main = blackBoard['settings'][0]
        
        
        self.assertEqual( build_css.createMainRule(main, "Blackboard"),
            ("pre.Blackboard, pre.Blackboard .lineNumber {\n"
             "    background-color: #0C1021;\n"
             "    color: #F8F8F8;\n"
             "}"),
        )
            
    def test_createScopeRule(self):
        comment = blackBoard['settings'][1]
        self.assertEqual( comment['name'], "Comment" )
        
        
        self.assertEqual( build_css.createScopeRule(comment, "Blackboard"),
            ("pre.Blackboard .Comment {\n"
             "    color: #AEAEAE;\n"
             "}"),
        )
    
    def test_getCSSFromTMSettings(self):
        main = blackBoard['settings'][0]['settings']
        
        self.assertEqual (build_css.getCSSFromTMSettings(main),
            [("background-color","#0C1021"), ("color","#F8F8F8")]
        )
    
    def test_getCSSFromThemeDict(self):
        self.assertTrue (
            build_css.getCSSFromThemeDict(blackBoard).startswith (
                ("pre.Blackboard, pre.Blackboard .lineNumber {\n"
                 "    background-color: #0C1021;\n"
                 "    color: #F8F8F8;\n"
                 "}")
            )
        )
    
if __name__ == "__main__":
    unittest.main()