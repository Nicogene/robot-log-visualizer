#! /bin/bash
echo "Generate the main window"
pyuic5 -o ui/autogenerated/visualizer.py ui/misc/visualizer.ui

echo "Generate About"
pyuic5 -o  ui/autogenerated/about.py ui/misc/about.ui

pyuic5 -o  ui/autogenerated/plot_tab.py ui/misc/plot_tab.ui

echo "The ui is generated"
