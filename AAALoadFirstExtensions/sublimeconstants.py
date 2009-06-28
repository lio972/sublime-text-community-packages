#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

import re

################################################################################

RE_SPECIAL_CHARS = re.compile (
    '(\\\\|\\*|\\+|\\?|\\||\\{|\\}|\\[|\\]|\\(|\\)|\\^|\\$|\\.|\\#|\\ )' )

################################################################################

CTAGS_LANG_SCOPE = {
    'C'          : 'source.c',
    'C++'        : 'source.c++',
    'C#'         : 'source.css',
    'Erlang'     : 'source.erlang',
    'HTML'       : 'text.html.basic',
    'Java'       : 'source.java',
    'JavaScript' : 'source.js',
    'Lisp'       : 'source.lisp',
    'Lua'        : 'source.lua',
    'Make'       : 'source.makefile',
    'Perl'       : 'source.perl',
    'PHP'        : 'source.php',
    'Python'     : 'source.python',
    'Ruby'       : 'source.ruby',
    'SQL'        : 'source.sql',
    'Sh'         : 'source.shell',

    'SML'        : None,
    'Asm'        : None,
    'Asp'        : None,
    'Awk'        : None,
    'Basic'      : None,
    'BETA'       : None,
    'Fortran'    : None,
    'Cobol'      : None,
    'Eiffel'     : None,
    'Pascal'     : None,
    'REXX'       : None,
    'Scheme'     : None,
    'SLang'      : None,
    'Tcl'        : None,
    'Vera'       : None,
    'Verilog'    : None,
    'Vim'        : None,
    'YACC'       : None
}

################################################################################

SYNTAX_SCOPE_MAP = {
'C#/Build.tmLanguage'                          : 'source.nant-build',
'C#/C#.tmLanguage'                             : 'source.cs',

'C++/C++.tmLanguage'                           : 'source.c++',
'C++/C.tmLanguage'                             : 'source.c',

'CSS/CSS.tmLanguage'                           : 'source.css',
'D/D.tmLanguage'                               : 'source.d',
'Default/Sublime Options.tmLanguage'           : 'source.sublime-options',

'Erlang/Erlang.tmLanguage'                     : 'source.erlang',
'Erlang/HTML (Erlang).tmLanguage'              : 'text.html.erlang.yaws',

'Genshi/Genshi-Template-(Text).tmLanguage'     : 'text.plain.genshi',
'Genshi/Markup-Template-(HTML).tmLanguage'     : 'text.html.genshi',
'Genshi/Markup-Template-(XML).tmLanguage'      : 'text.xml.genshi',

'Graphviz/DOT.tmLanguage'                      : 'source.dot',
'Groovy/Groovy.tmLanguage'                     : 'source.groovy',
'HTML/HTML.tmLanguage'                         : 'text.html.basic',

'Haskell/Haskell.tmLanguage'                   : 'source.haskell',
'Haskell/Literate Haskell.tmLanguage'          : 'text.tex.latex.haskell',

'Highlighter/Highlighter.tmLanguage'           : 'source.shell',

'Java/Java.tmLanguage'                         : 'source.java',
'Java/JavaDoc.tmLanguage'                      : 'text.html.javadoc',
'Java/JavaProperties.tmLanguage'               : 'source.java-props',

'JavaScript.tmbundle/JavaScript.tmLanguage'    : 'source.js',

'LaTeX/Bibtex.tmLanguage'                      : 'text.bibtex',
'LaTeX/LaTeX Beamer.tmLanguage'                : 'text.tex.latex.beamer',
'LaTeX/LaTeX Log.tmLanguage'                   : 'text.log.latex',
'LaTeX/LaTeX Memoir.tmLanguage'                : 'text.tex.latex.memoir',
'LaTeX/LaTeX.tmLanguage'                       : 'text.tex.latex',
'LaTeX/TeX Math.tmLanguage'                    : 'text.tex.math',
'LaTeX/TeX.tmLanguage'                         : 'text.tex',

'Lisp/Lisp.tmLanguage'                         : 'source.lisp',
'Lua/Lua.tmLanguage'                           : 'source.lua',
'Makefile/Makefile.tmLanguage'                 : 'source.makefile',

'Markdown/Markdown.tmLanguage'                 : 'text.html.markdown',
'Markdown/MultiMarkdown.tmLanguage'            : 'text.html.markdown.multimarkdown',

'Matlab/Matlab.tmLanguage'                     : 'source.matlab',

'OCaml/OCaml.tmLanguage'                       : 'source.ocaml',
'OCaml/OCamllex.tmLanguage'                    : 'source.ocamllex',
'OCaml/OCamlyacc.tmLanguage'                   : 'source.ocamlyacc',
'OCaml/camlp4.tmLanguage'                      : 'source.camlp4.ocaml',

'PHP/PHP.tmLanguage'                           : 'source.php',
'Perl/Perl.tmLanguage'                         : 'source.perl',
'Python/Python.tmLanguage'                     : 'source.python',

'R/R Console.tmLanguage'                       : 'source.r-console',
'R/R.tmLanguage'                               : 'source.r',
'R/Rd (R Documentation).tmLanguage'            : 'text.tex.latex.rd',

'Rails/HTML (Rails).tmLanguage'                : 'text.html.ruby',
'Rails/Ruby on Rails.tmLanguage'               : 'source.ruby.rails',
'Rails/SQL (Rails).tmLanguage'                 : 'source.sql.ruby',

'Regular Expressions/RegExp.tmLanguage'        : 'source.regexp',
'RestructuredText/reStructuredText.tmLanguage' : 'text.restructuredtext',
'Ruby/Ruby.tmLanguage'                         : 'source.ruby',
'SQL/SQL.tmLanguage'                           : 'source.sql',
'ShellScript/Shell-Unix-Generic.tmLanguage'    : 'source.shell',

'TCL/HTML (Tcl).tmLanguage'                    : 'text.html.tcl',
'TCL/Tcl.tmLanguage'                           : 'source.tcl',

'Text/Plain text.tmLanguage'                   : 'text.plain',

'Textile/Textile.tmLanguage'                   : 'text.html.textile',

'XML/XML.tmLanguage'                           : 'text.xml',
'XML/XSL.tmLanguage'                           : 'text.xml.xsl'
}

################################################################################

SCOPE_PACKAGE_MAP = dict (
    (v, k.split('/')[0]) for (k, v) in SYNTAX_SCOPE_MAP.items() )

################################################################################

SYMBOLIC_BINDINGS =  [ 'backquote', 'backslash', 'backspace',
                       'browser_back', 'browser_favorites', 'browser_forward',
                       'browser_home', 'browser_refresh', 'browser_search',
                       'browser_stop', 'capslock', 'clear', 'comma',
                       'contextmenu', 'delete', 'down', 'end', 'enter',
                       'equals', 'escape', 'home', 'insert', 'left',
                       'leftalt', 'leftbracket', 'leftcontrol', 'leftmeta',
                       'leftshift', 'leftsuper', 'minus', 'numlock',
                       'pagedown', 'pageup', 'pause', 'period', 'printscreen',
                       'quote', 'right', 'rightalt', 'rightbracket',
                       'rightsuper', 'scrolllock', 'semicolon', 'slash',
                       'space', 'tab', 'up' ]

LITERAL_SYMBOLIC_BINDING_MAP = {
    '\\'   :  'backslash',
    ','    :  'comma',
    '='    :  'equals',
    '['    :  'leftbracket',
    '-'    :  'minus',
    '.'    :  'period',
    '\''   :  'quote',
    ']'    :  'rightbracket',
    ''     :  'rightsuper',
    ';'    :  'semicolon',
    '/'    :  'slash',
    ' '    :  'space',
}

################################################################################