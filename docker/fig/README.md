Install Fig::

    $ sudo pip install -U fig

Before you begin
----------------

Update the appropriate fig file being used with the appropriate credentials.

Warning - never git commit your secret credentials to upstream!  We recommend you create a new file named fig_local.yml (this will be ignored by git) and add your credentials in there.  Reference that file in the -f parameter in the instructions below.


Install Poppy from Upstream (fig.yml)
-------------------------------------

Build and Run::

    $ fig up -f fig_local.yml -d

Build && Rebuild::

    $ fig -f fig_local.yml build

To stop all your fig containers::

    $ fig stop

To start all your fig containers without rebuilding::

    $ fig start

To get the most-updated code of poppy::

    $ fig run poppy git --git-dir=/home/poppy/.git pull
    $ fig run poppy uwsgi --reload /var/run/poppy/poppy.pid


Mounting a local Poppy Volume (copy from fig_dev.yml)
-------------------------------------------

1. Build and Run::

    $ ./docker/fig/dev -f fig_local.yml up -d

Note that `dev` is a wrapper around the [`fig` CLI](http://www.fig.sh/cli.html) so
any sub-commands that work with the fig CLI will work with `dev` as well.

Also note that the `fig_dev.yml` file in this folder cannot be used directly with
`fig`. Please invoke `dev` instead as it does some extra setup before internally
invoking `fig`.


Building and Running the Poppy API Server w/Mimic (fig_mimic.yml)
-----------------------------------------------------------------

From this folder, run:

    $ ./docker/fig/dev_mimic -f fig_local.yml up -d

This will bring up a poppy server with your local poppy repository mounted as a volume
and will run it with any local changes. Cassandra and Mimic will also be started and
wired together.

If you are running docker locally, you can then access the API at:

    $ curl http://<docker_ip>/v1.0/

If local changes are made, simply restart the services to run them:

    $ ./docker/fig/dev_mimic restart

You can run the API tests against the poppy container according to the
[API testing](https://github.com/stackforge/poppy/blob/master/tests/api/README.rst)
documentation.

Note that `dev_mimic` is a wrapper around [`fig`](http://www.fig.sh/cli.html) so
any sub-commands that work with the fig CLI will work with `dev_mimic` as well.

Note that `dev_mimic` does not run a repose container.


Testing
--------

Access the running poppy api instance home document::

    $ curl <docker_ip>/v1.0/
