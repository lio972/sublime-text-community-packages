LaTeX Package for Sublime Text
==============================

First draft "release" September 21, 2009

Current revision October 2, 2009

Contributors:
Marciano Siniscalchi
(more to come I hope!)


Introduction
------------

This package provides support for editing TeX / LaTeX files, emulating functionality
in TextMate's well-known LaTeX bundle. Like its TextMate counterpart, it is designed with the creation of *PDF* rather than *DVI* output in mind.

While it is not(yet!) as powerful as its TextMate counterpart, it does offer a number of convenient features:
	
* A command to run tex & friends, and then show the user any errors that might have occurred
* A command to view the PDF file, setting things up so that **PDF inverse search** works (see below for details)
* Quick insertion of Greek letters and other LaTeX macros, e.c. `\sum`, `\bigcup` etc.
* Insertion of references (`\ref{xxx}`) and citations (`\cite{xxx}`), listing the available labels or, respectively, keys in a pop-up menu or quick-panel
* Closing the current environment
* Inserting emphasize / boldface commands (more in the future)
	
The most useful feature is probably PDF inverse search. The TeX/LaTeX world has moved beyond DVI; on the Mac, PDF output is the default for LaTeX documents, thanks to excellent built-in support for PDF rendering, and several great PDF previewers. The "SyncTeX" technology has finally brought reliable forward- and inverse-search to PDF documents. Luckily, SyncTeX is built into MikTeX from version 2.7 up, and
the [SumatraPDF][] previewer. The same technology is also used by TextMate and the Skim
previewer on the Mac, and makes for a much more efficient and
enjoyable texing experience. You can double-click anywhere in the PDF
window, and you jump right back to the corresponding point in the
source tex file. This is a *huge* time saver! Sublime Text has a very
sane command-line syntax, which makes it relatively easy to implement
this feature.

Forward search is a planned feature (DDE communication with SumatraPDF is required).

[SumatraPDF]: http://blog.kowalczyk.info/software/sumatrapdf/ "SumatraPDF"

All commands are available both via keyboard shortcuts and from the `Tools|Packages|LaTeX Package` menu. (Invoking snippets from the menu does not seem to work right now: use the tab trigger)

Compiling and viewing your document
-----------------------------------

###Commands and Shortcuts 

texify : `ctrl+alt+t`

showTeXErrors :	`ctrl+alt+e`

viewPDF : `ctrl+alt+v`


###Explanation

The "texify" command compiles the file in the current buffer, invoking `texify`
(which in turn takes care of invoking e.g. `bibtex`, `makeindex`, etc. as needed).
Furthermore, it sets up inverse search with the SumatraPDF previewer, using
the SyncTeX technology. 

The previewer is *not* automatically started; use the viewPDF command.

If errors or warnings are detected, a quick panel is shown with a list of
"helpful" messages taken from tex's log file. Click on any line that contains a
line number, and you will be taken to the offending line. The quick-panel is
closed upon clicking one line, but you can reopen it via the "showTeXErrors"
command.

###Requirements

* MiKTeX distribution at <http://www.miktex.org>; I have ver. 2.7; ver. 2.8 also works
* SumatraPDF previewer, ver. 0.93, 0.94 or recent preview release
 at <http://blog.kowalczyk.info/software/sumatrapdf/>
* Make sure that both SumatraPDF and Sublime Text are on the `%PATH%`


Easy insertion of tex math macros
---------------------------------

###Shortcuts

texMacro : `ctrl+shift+\`

This feature is also inspired by TextMate's LaTeX bundle, and implemented
stealing ideas from the html snippets. I used the Textmate keybindings, but
that can (and perhaps should) be changed. Basic idea, using Sublime Text
notation `key1, key2+key3` to mean "press `key1`, then press `key2` and `key3`
simultaneously":

`a, ctrl+backslash` gives `\alpha`

`b, ctrl+backslash` gives `\beta`

...

`A, ctrl+backslash` gives `\forall`

etc. Look at the `texMacro.py` file for a complete list of available shortcuts. You can also add your own shortcuts to the `macros` Python dictionary. Your shortcut can consists of letters or numbers, without spaces or other symbols. Remember to escape the leading backslash.


References and citations
------------------------

###Shortcuts

texRef : `ctrl+alt+r`

texCite : `ctrl+alt+c`


This is functionality that might perhaps be achieved with ctags. Suppose you
have something like:


	\begin{lemma} \label{lem:result}
	...
	\end{lemma}

in your file. You then need to reference this lemma later on. Invoke the
texRef command and pick from the list. In particular, if you begin writing
`lem` and then hit `ctrl+alt+r`, only labels beginning with "lem" are shown. The
`\ref{...}` command is NOT automatically inserted for you. So, the typical use
case is to enter `\ref{` (which generates a matching `}` and places the cursor
in between the braces), hit `ctrl+alt+r`, and choose the label. 

If there are no more than 16 matches, then a pop-up completion menu is shown; otherwise, the quick panel will list all matches. 

Similarly for citations: entries, however, are drawn from a bibtex file
(specified by the `\bibliography` command in your tex file). This pops up a
quick panel that shows both the key and the title of the article or book.
The `\cite{...}` command is automatically inserted, and the word `cite` is
highlighted so you can change it to, e.g. `citep` or `citet` if you use
natbib. Hitting Tab moves you after the closing brace.

There is an attempt to handle multiple cites; if you start a cite command, then type a comma, as in

	\cite{mycite1,}


and invoke texCite again, the quick panel is shown with a list of all citations. But if you try to provide a prefix, it won't work.



Environment closer
------------------

###Shortcuts:

latexEnvCloser : `ctrl+alt+.`

Looks for the last `\begin{...}` that is not matched by the corresponding `\end{...}`, and inserts the `\end{...}` statement automatically. It also checks for mismatched `begin/end` pairs, just in case.


Insert command or environment based on current word
---------------------------------------------------

###Shortcuts:
	
latexEnvironment : `ctrl+shift+[`

latexCommand : `ctrl+shift+]`

Type `test`, invoke latexCommand, get `\test{}` with the cursor between braces; type something, then hit Tab to exit the braces. Similarly, type `test`, invoke latexEnvironment, get 

	\begin{test}
	
	\end{test}

with the cursor inside the environment. Again, Tab exits the environment.


Miscellaneous commands/snippets
-------------------------------

"Emphasize" (`e,m,tab`) enters `\emph{}` and drops the cursor between the
braces. Hit tab to exit the braces.

"Boldface" does the same, but enters `\textbf{}`.
