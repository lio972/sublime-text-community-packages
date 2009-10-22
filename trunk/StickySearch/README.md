# StickySearch 

allows you to highlight search items, regardless of your normal (ctrl+f) search items. this plug-in search items will be kept highlighted till you manually dismiss them.

you can add markers, you can reset and clear markers. 

## dependencies

this plug-in is using an experimental sublime text API, exposed on 20091017 beta.

to define what color you want to see for the marked text, you should edit your theme file, and add the following:
	
	<dict>
		<key>name</key>
		<string>Marker</string>
		<key>scope</key>
		<string>marker</string>
		<key>settings</key>
		<dict>
			<key>fontStyle</key>
			<string></string>
			<key>foreground</key>
			<string>#FFFF77</string>
		</dict>
	</dict>	
	
# Usage

This is the official binding:
	
	<bindings>
		<!-- sticky search -->
		<binding key="ctrl+shift+keypad_multiply" command="stickySearch set" />
		<binding key="ctrl+shift+keypad_plus" command="stickySearch add" />
		<binding key="ctrl+shift+keypad_minus" command="stickySearch clear" />
	</bindings>
	
* 'set' will mark the new item, after clearing the old markers
* 'add' will mark the new item, leaving other marking as they were
* 'clear' will clean all the markings