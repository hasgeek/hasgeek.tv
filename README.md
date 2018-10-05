HasGeek TV
==========

Source for [HasGeek TV](http://hasgeek.tv).

This project is a work in progress.


Test deployment
---------------

Here is how you make a test deployment:

    $ git clone https://github.com/hasgeek/hasgeek.tv.git
    $ cd hasgeek.tv
    $ cp instance/settings-sample.py instance/settings.py
    $ vim instance/settings.py # Customize this file as needed
    $ pip install -r requirements.txt
    $ python runserver.py


## Asset builds

To build for production:

```
make assets
```

or if `make` is not available,

```
cd hgtv/assets
npm install
npm run build
```
