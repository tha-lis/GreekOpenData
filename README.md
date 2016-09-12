### Plugin Builder Results

Congratulations! You just built a plugin for QGIS!

Your plugin **GreekOpenData** was created in:
   **C:\\Users\\thanos\\.qgis2\\python\\plugins\\GreekOpenData**
Your QGIS plugin directory is located at:
   **C:/Users/thanos/.qgis2/python/plugins**

### What's Next

1.  In your plugin directory, compile the resources file using pyrcc4 (simply run **make** if you have automake or use **pb\_tool**)
2.  Test the generated sources using **make test** (or run tests from your IDE)
3.  Copy the entire directory containing your new plugin to the QGIS plugin directory (see Notes below)
4.  Test the plugin by enabling it in the QGIS plugin manager
5.  Customize it by editing the implementation file **GreekOpenData.py**
6.  Create your own custom icon, replacing the default **icon.png**
7.  Modify your user interface by opening **GreekOpenData\_dialog\_base.ui** in Qt Designer

Notes:
-   You can use the **Makefile** to compile and deploy when you make changes. This requires GNU make (gmake). The Makefile is ready to use, however you will have to edit it to add addional Python source files, dialogs, and translations.
-   You can also use **pb\_tool** to compile and deploy your plugin. Tweak the *pb\_tool.cfg* file included with your plugin as you add files. Install **pb\_tool** using *pip* or *easy\_install*. See <http://loc8.cc/pb_tool> for more information.

For information on writing PyQGIS code, see <http://loc8.cc/pyqgis_resources> for a list of resources.

![GeoApt LLC](http://geoapt.com/geoapt_logo_p.png "GeoApt LLC") ©2011-2015 GeoApt LLC - geoapt.com
