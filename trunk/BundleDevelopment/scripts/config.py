################################################################################

import optparse

################################################################################

OUTPUT_PACKAGES_PATH = ur'E:\Sublime\sublime-text-community-packages\ConvertedTextMateSnippets'

TM_BUNDLES_PATH = "E:\\Sublime\\tmbundles4win\\Bundles\\"

# OUTPUT_PACKAGES_PATH = ur'/home/wazoocom/converted-textmate-snippets'

# TM_BUNDLES_PATH = "/home/wazoocom/TextMate/Bundles"

################################################################################
# Cmd Line Option Parser

opt_parser = optparse.OptionParser()

opt_parser.add_option (
     "-i",  "--input", metavar = "DIR",
     help   = "TextMate bundles path (containing *.tmbundle)",
     default =  TM_BUNDLES_PATH )

opt_parser.add_option (
     "-o",  "--output", metavar = "DIR",
     help    = "Output path",
     default = OUTPUT_PACKAGES_PATH )

opt_parser.add_option (
     "-c",  "--contextual", action = 'store_true',
     help    = "Use contextual keybindings for tab\n"
               "triggers. Requires use of plugin" )

opt_parser.add_option (
     "-s",  "--syntax", action = 'store_true',
     help    = "Copy in syntax files "
               "as well as convert snippets",
     default = False )

opt_parser.add_option (
     "-t",  "--test", action = 'store_true',
     help   = "run tests" )

################################################################################