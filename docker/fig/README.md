Install Fig::

    $ sudo pip install -U fig


Install Poppy from Upstream
---------------------------

Build and Run::

    $ fig up -d

Build && Rebuild::

    $ fig build

To stop all your fig containers::

    $ fig stop

To start all your fig containers without rebuilding::

    $ fig start

To get the most-updated code of poppy::

    $ fig run poppy git --git-dir=/home/poppy/.git pull
    $ fig run poppy uwsgi --reload /var/run/poppy/poppy.pid


Mounting a local Poppy Volume
-----------------------------

1. Build and Run::

    $ dev up

Note that `dev` is a wrapper around the [`fig` CLI](http://www.fig.sh/cli.html) so
any sub-commands that work with the fig CLI will work with `dev` as well.

Also note that the `fig_dev.yml` file in this folder cannot be used directly with
`fig`. Please invoke `dev` instead as it does some extra setup before internally
invoking `fig`.


Testing
--------

Access the running poppy api instance home document::

    $ curl <docker_ip>/v1.0/
