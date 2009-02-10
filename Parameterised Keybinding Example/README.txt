This is an example of what you can do with parameterised keybindings in Sublime Text. 

This example was created from an example posted by Jon Skinner, developer of Sublime Text. Here's the original post in which Jon introduces the feature.

----

Sublime Text has had 'parameterised keybindings' for some time, enabling one key binding be an input for another.

The key binding file below best describes it. Firstly, it hijacks alt+letter keys for first person shooter inspired cursor movement: `Alt+WSAD` move the cursor up/down and left/right by words. `Alt+QE` move to the beginning and end of line, and `Alt+ZC` move forwards and back by characters. There are a few other movement related bindings in the surrounding keys, too.

On the right hand side of the keyboard are some vi-style commands. Alt+J, followed by one of the above movement keys, will delete text till that point. For example, pressing `Alt+J,A` will delete a word to the left of the cursor. `Alt+J,E` will delete till the end of the line. As well as delete, there are a few other commands for copying a region of text, and pasting it at a given location.

It's worth having a play around with at any rate, not having to use the arrow keys for cursor navigation at the least is worth the price of entry.

    <bindings>
       <binding key="alt+a" command="move words -1"/>
       <binding key="alt+d" command="move words 1"/>
       <binding key="shift+alt+a" command="move words -1 extend"/>
       <binding key="shift+alt+d" command="move words 1 extend"/>
       <binding key="alt+z" command="move characters -1"/>
       <binding key="alt+c" command="move characters 1"/>
       <binding key="shift+alt+z" command="move characters -1 extend"/>
       <binding key="shift+alt+c" command="move characters 1 extend"/>
       <binding key="alt+w" command="move lines -1"/>
       <binding key="alt+s" command="move lines 1"/>
       <binding key="shift+alt+w" command="move lines -1 extend"/>
       <binding key="shift+alt+s" command="move lines 1 extend"/>
       <binding key="alt+x" command="expandSelectionTo line"/>
       <binding key="shift+alt+x" command="expandSelectionTo line"/>
       <binding key="alt+q" command="moveTo bol"/>
       <binding key="alt+e" command="moveTo eol"/>
       <binding key="shift+alt+q" command="moveTo bol extend"/>
       <binding key="shift+alt+e" command="moveTo eol extend"/>
       <binding key="alt+r" command="moveTo bof"/>
       <binding key="alt+f" command="moveTo eof"/>
       <binding key="shift+alt+r" command="moveTo bof extend"/>
       <binding key="shift+alt+f" command="moveTo eof extend"/>
       
       <binding key="alt+i" command="repeat"/>
       <binding key="alt+j" command="deleteOver ${motion}"/>
       <binding key="alt+l" command="cutOver ${motion}"/>
       <binding key="alt+k" command="copyOver ${motion}"/>
       <binding key="alt+semicolon" command="paste"/>
       <binding key="alt+p" command="pasteAt ${motion}"/>
       <binding key="alt+o" command="copy"/>
       
       <namespace name="motion">
          <binding key="alt+a" command="words -1"/>
          <binding key="a" command="words -1"/>
          <binding key="alt+d" command="words 1"/>
          <binding key="d" command="words 1"/>
          <binding key="alt+z" command="characters -1"/>
          <binding key="z" command="characters -1"/>
          <binding key="alt+c" command="characters 1"/>
          <binding key="c" command="characters 1"/>
          <binding key="alt+w" command="lines -1"/>
          <binding key="w" command="lines -1"/>
          <binding key="alt+s" command="lines 1"/>
          <binding key="s" command="characters 1"/>
          <binding key="alt+x" command="entireline"/>
          <binding key="x" command="entireline"/>
          <binding key="alt+q" command="bol"/>
          <binding key="q" command="bol"/>
          <binding key="alt+e" command="eol"/>
          <binding key="e" command="eol"/>
          <binding key="alt+r" command="moveTo bof"/>
          <binding key="r" command="moveTo bof"/>
          <binding key="alt+f" command="moveTo eof"/>
          <binding key="f" command="moveTo eof"/>
       </namespace>
    </bindings>

You can see the parametrisation in action by looking at the commands like: 

    <binding key="alt+j" command="deleteOver ${motion}"/>
    
The `${motion}` indicates that the next key binding is expected to one of the entries in the 'motion' namespace, and the text `${motion}` will be replaced by the text of the next entered command.