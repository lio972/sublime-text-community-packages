This package contains two plugins: Refresher and Live Preview

# Refresher

Will launch Internet Explorer and Firefox, and refresh on every save. Internet Explorer will automatically "follow" firefox, so there is no need to copy and paste urls between the two. Refresher is useful for when working with PHP etc and dynamically generated html.

`ctrl-alt-i` to launch browsers
ctrl-alt-shift-i to swap between the two

# Live Preview

This is for static basic html (not php/javascript). It uses COM to communicate with Internet Explorer, updating the buffer "as you type". There are markdown and textile modes. Just set the syntax type for the view to either.

see:  http://blogdata.akalias.net/live_preview/live_preview.htm

ctrl-shift-p to launch live preview or toggle visibility if already running.

# Problems with annoying javascript/activex prompt?

![tools allow](http://www.menumachine.com/kb/images/activeX_toolsallow.gif)

# Dependencies

This package depends on the SublimeExtensions package ( available from sublime community svn repo )