This is an extension of the tool built by David Stansby wherein I added the PHI instrument blos data products and the heliograpic latitude plot.

Solar Orbiter Data Availability (SODA)
======================================

A tool to visualise the data availability of Solar Orbiter data products.
The dashboard can be viewed at https://www.davidstansby.com/soda/.

Usage
-----

`python run_soda.py` will run SODA, and create an updated static `index.html` file that can be uploaded to a server.

Automatic deployment
--------------------
Github actions automatically deploys a new HTML file to the `pages` branch
every time a commit is pushed to the main branch.
