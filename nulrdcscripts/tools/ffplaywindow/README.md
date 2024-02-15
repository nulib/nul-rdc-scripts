# General Information

Version Date: 2/13/2024

Document Owner: Sophia Francis

Software Used: ffplay

# Description
This is a script that allows for the playback of video files with vectorscope, waveform monitor, BRNGout detector. The command that is used is originally from VRecord and this script just serves as a method of utilizing it without VRecord and from the command line.


# Installation Instructions
This script runs through poetry and can be installed and updated from it. 

## Usage
To run the script. From nul-rdc-scripts
```
poetry run ffplaywindow -i \path\to\input
```
To change the highlight color for the BRNG filter. Use -hi or --highlight followed by color name or hexcode.
```
poetry run ffplaywindow -i \path\to\input -hi 'color name or hexcode'
```

- To exit playback window, use the esc key
- To fast-forward or rewind use the arrow keys.
- To pause or unpause press the space bar


### Supported Highlight Colors
You can use any hexcode (with alpha addition -- or just tack on '0x' before the hexcode) you wish for changing the color of the highlight. 

Here are a few that are suggested from FFMPEGs color swatches that are visible enough to be used.

#### Note: There should be no space between parts of the color name (any in this chart are a mis-type)
![Aqua, Aquamarine, Blue, BlueViolet, Brown, CadetBlue, Chartreuse, Coral, Cornflower, Crimson, DarkBlue, DarkCyan, DarkGoldenRod, DarkGreen, DarklMagenta, DarkOliveGreen, DarkOrange, DarkOrchid, DarkRed, DarkSalmon, DarkSeaGreen, DarkSlateBlue, DarkTurquoise, DarkViolet, DeepPink, DeepSkyBlue, DodgerBlue, Firebrick, ForestGreen, Fuchisa, Gold, GoldenRod, Green, GreenYellow, HotPink, Indigo, LawnGreen, LimeGreen, Maroon, Navy, Olive, OliveDrab, Orange, OrangeRed, Orchid, Purple, Red, RoyalBlue, SaddleBrown, SeaGreen, Teal, Tomato, Turquoise, Yellow](/docs/images/ColorsForFFMPEG.png)
