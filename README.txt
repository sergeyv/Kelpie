Buildout for repoze.bfg
=======================

This buildout builds repoze.bfg for users who have trouble installing
repoze.bfg via ``easy_install`` because ``lxml`` won't compile against
their system versions of ``libxml2`` and ``libxslt``.

Using buildout is slightly different than using ``easy_install`` for
the same purpose so we document installation of ``repoze.bfg`` and the
creation and subsequent registration of a new application here for
people who need to run this way.

Installing
----------

Download virtualenv from http://pypi.python.org/pypi/virtualenv and
install it into your system Python.  Once you've installed it, create
a virtualenv like so:

  $ $PYTHONHOME/bin/virtualenv --no-site-packages ~/env

Where $PYTHONHOME/bin is where your Python installation installs its
scripts.  This will create a virtualenv in a subdirectory of your home
directory named "env".

Subsequently, check this package out of Subversion:

  $ svn co http://svn.repoze.org/buildouts/repoze.bfg/trunk bfg

After you've succesfully checked it out, nvoke the buildout via:

  $ cd bfg
  $ ~/env/bin/python bootstrap.py
  $ bin/buildout -U

.. warning:: The ``-U`` flag above is *very important*.  It specifies
   to buildout that it should ignore the ``~/.buildout/default.cfg``
   file, which is often trampled upon by other software in ways that
   are incompatible with :mod:`repoze.bfg`'s usage of buildout.

When it's finished, ``libxml2`` and ``libxslt`` should have been
downloaded and compiled, and ``lxml`` should have been built against
these versions.  All required bfg software should also be installed
within the buildout environment.

If the buildout doesn't finish successfully due to a compilation
error, make sure you have gcc configured on your system and make sure
you have the Python development libraries installed.  For Debian-based
systems, this means installing the ``build-essentials`` and
``python-devel`` (or perhaps ``python-dev``) packages.  For Mac OS X
users, this means having XCode Tools installed.  Then try again.

Running
-------

The docs for creating a project at
http://static.repoze.org/bfgdocs/narr/project.html, need to be amended
slightly to account for a buildout-based installation.

To create a project, use the ``bin/paster`` script in the buildout
directory instead of your "main" Python's ``paster``::

  $ bin/paster create -t bfg_starter

Name the project "myproject" when asked.  A directory named
``myproject`` will be created in the buildout directory.

Edit the ``buildout.cfg`` file and add the following to the file's
``[buildout]`` section::

  develop = myproject

Add a line to the "eggs" value in the ``[bfg]`` section of the
buildout so that it looks like so::

  eggs = repoze.bfg
         myproject

The resulting diff to the buildout.cfg file on my sistem looks like this::

  ===================================================================
  --- buildout.cfg        (revision 1573)
  +++ buildout.cfg        (working copy)
  @@ -6,6 +6,8 @@
        lxml
        bfg
   
  +develop = myproject
  +
   [lxml-environment]
   XSLT_CONFIG=${buildout:directory}/parts/libxslt/bin/xslt-config
   XML2_CONFIG=${buildout:directory}/parts/libxml2/bin/xml2-config
  @@ -46,6 +48,7 @@
   [bfg]
   index = http://dist.repoze.org/lemonade/dev/simple
   recipe = repoze.recipe.egg
  -eggs = repoze.bfg
  +eggs = repoze.bfg 
  +       myproject
   interpreter = python-bfg

You can run ``svn diff`` to compare this to yours to see if you got it
right.
 
Once you've added ``myproject`` to buildout.cfg, run ``bin/buildout``
to set up your new project in the buildout environment.  Success looks
like this in the output of ``bin/buildout``:

  [chrism@oops trunk]$ bin/buildout 
  Develop: '/Users/chrism/projects/repoze/svn/buildouts/repoze.bfg/trunk/myproject'
  Updating libxml2.
  Updating libxslt.
  Updating lxml.
  Installing bfg.
  Generated script '/Users/chrism/projects/repoze/svn/buildouts/repoze.bfg/trunk/bin/paster'.
  buildout: Generated interpreter '/Users/chrism/projects/repoze/svn/buildouts/repoze.bfg/trunk/bin/python-bfg'.

You should then be able to run ``bin/paster serve
myproject/myproject.ini`` and visit the running application at
http://127.0.0.1:6543 in a browser.  Success looks like this::

  [chrism@oops trunk]$ bin/paster serve myproject/myproject.ini 
  Starting server in PID 6073.
  serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

The ``bin/python-bfg`` command within the buildout directory will
invoke an interactive Python prompt with all the bfg dependencies
available for import.  You should use this command, e.g. to run
the ``setup.py test`` of your application, should you write tests.

From this point on you should be able to pick up and use the docs
beginning with
http://static.repoze.org/bfgdocs/narr/project.html#the-project-structure
.
