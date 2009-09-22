LaTeX Package for Sublime Text
------------------------------

First draft "release" September 21, 2009

Contributors:
Marciano Siniscalchi
(more to come I hope!)


These are the beginnings of a package that will, in time, provide full support
for editing TeX / LaTeX files, emulating functionality provided by TextMate's
well-known LaTeX bundle.

Relative to the LaTeX package that comes with ver. 1.2 of Sublime Text, it
offers the following improvements.

1. Cleaned up snippets. 

Some snippets (e.g. the \[ ...\] snippet) did not work, i.e. only inserted
[...], because the backslash was not escaped in the .sublime-snippet file. I
fixed these minor issues. Not a biggie obviously.


2. "texify", "showTeXErrors" and "viewPDF" commands.

The "texify" command compiles the file in the current buffer, invoking texify
(which in turn takes care of invoking e.g. bibtex, makeindex, etc. as needed).
Furthermore, it sets up INVERSE SEARCH with the SumatraPDF previewer, using
the SyncTeX technology. This is also used by TextMate and the Skim previewer
on the Mac, and makes for a much more efficient and enjoyable texing
experience. You can double-click anywhere in the PDF window, and you jump
right back to the corresponding point in the source tex file.

The previewer is NOT automatically started; use the viewPDF command.

If errors are detected, a quick panel is shown with a list of "helpful" error
messages taken from tex's log file. Click on any line that contains a line
number, and you will be taken to the offending line. The quick-panel is closed
upon clicking one line, but you can reopen it via the showTeXErrors command.


REQUIRES: 
* MiKTeX distribution (www.miktex.org); I have ver. 2.7; ver. 2.8 also works
* SumatraPDF previewer, ver. 0.93, 0.94 or recent preview release
 (http://blog.kowalczyk.info/software/sumatrapdf/)
* Make sure that both SumatraPDF and Sublime Text are on the %PATH%

SHORTCUTS: ctrl+alt+t (texify), ctrl+alt+e (show tex errors)


3. easy insertion of tex math macros.

Again, this feature is inspired by TextMate's LaTeX bundle, and implemented
stealing ideas from the html snippets. I used the Textmate keybindings, but
that can (and perhaps should) be changed. Basic idea, using Sublime Text
notation "key1, key2+key3" to mean "press key1, then press key2 and key3
simultaneously":

a, ctrl+backslash gives \alpha
b, ctrl+backslash gives \beta
...
A, ctrl+backslash gives \forall

etc. Look at the "texMacro.py" and "Default.sublime-keymap" files for details.
If you want to add your own macros, remember that the first match is used in
the keymap. This is why, for instance, I have "lp" for "\left(" listed before
the single-letter commands, and "p" in particular; otherwise,
"l,p,ctrl+backslash" would yield "l\pi".


4. References and citations

This is functionality that might perhaps be achieved with ctags. Suppose you
have something like:

\begin{lemma} \label{lem:result}
...
\end{lemma}

in your file. You then need to reference this lemma later on. Invoke the
"texRef" command and pick from the list. In particular, if you begin writing
"lem" and then hit ctrl+alt+r, only labels beginning with "lem" are shown. The
"\ref{...}" command is NOT automatically inserted for you. So, the typical use
case is to enter "\ref{" (which generates a matching "}" and places the cursor
in between the braces), hit ctrl+alt+r, and choose the label. Notice that if
you have too many labels, only a few are shown (this is Sublime Text
functionality---I'm not clear how these are chosen).

Similarly for citations: entries, however, are drawn from a bibtex file
(specified by the \bibliography command in your tex file). This pops up a
quick panel that shows both the key and the title of the article or book.
The "\cite{...}" command is automatically inserted, and the words "cite" is
highlighted so you can change it to, e.g. "citep" or "citet" if you use
natbib.

This feature is still under heavy development, so handle it with care :-) and
let me know what is broken.

SHORTCUTS: ctrl+alt+r (reference), ctrl+alt+c (citation)


5. Miscellaneous commands/snippets:

"Emphasize" (e,m,tab) enters "\emph{}" and drops the cursor between the
braces. Hit tab to exit the braces.

"Boldface" does the same, but enters "\textbf{}".
