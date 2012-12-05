HasGeek.tv
==========

Source for [HasGeek.tv](http://hasgeek.tv).

This project is a work in progress.


Test deployment
---------------

Here is how you make a test deployment::

    $ git clone https://github.com/hasgeek/hasgeek.tv.git
    $ cd hasgeek.tv
    $ cp instance/settings-sample.py instance/settings.py
    $ open instance/settings.py # Customize this file as needed
    $ pip install -r requirements.txt
    $ python runserver.py
