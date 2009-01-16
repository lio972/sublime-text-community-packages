Bringing hyperlinking to text file navigation...

This plugin provides a simple hyperlinking facility, which allows you to create very lightweight, text-file-based wikis. 

# Getting Started

Here's how you use it; create a folder and add at least one file with a ".wiki" extension. say;

    \world_of_fruit
       \fruit.wiki
              
Now edit fruit.wiki:

     The apple is a fine fruit. So is the orange.
   
Put your cursor somewhere inside the word 'apple', like this;

     The ap|ple is a fine fruit. So is the orange.

Hit ctrl+alt+n (navigate). You'll be prompted to see if you want to create a new file, apple.wiki. If you say yes, apple.wiki is created and you can start editing it straight away. Easy!

# Longer Links

If you want to create a file with a longer name, you can enclose it in square brackets;

    Have you ever wondered about the [nutritional values of kiwis]?
    
Then you can use the same navigation keypress (ctrl+alt+n) to visit 'nutritional values of kiwis.wiki'
