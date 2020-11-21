# CAD and 3d Printing

Some references I've found on the web that are helpful when designing the
case:

* https://ultimaker.com/en/resources/52843-design-guidelines


# KiCAD tips/tricks

Export a BOM for Mouser

* Use the bom2grouped_csv plugin
* cut -d, -f2,6 output | sed "s/\"//g" | grep -v "^[0-9],*$" | grep -v MPN | sed "s/\(.*\),\(.*\)/\2 \1/"
* Use mouser's BOM import tool, paste in the text generated above


# Looking at both board and model simultaneously

* Export as VRML (with mm as units) from Kicad
* Use https://www.makexyz.com/convert/wrl-to-stl to convert to STL
* Import directly into Tinkercad


# Tips and tricks for 3d design of printed parts

* https://www.3dhubs.com/knowledge-base/enclosure-design-3d-printing-step-step-guide/
