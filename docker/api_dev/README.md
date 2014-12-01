Before Starting
---------------

The following files should exist in this folder before running Dockerfile
* docker_rsa (private key) -> public key should be published to the private git repo
* poppy.conf (desired configuration for poppy api)
* logging.conf (desired logging configuration file)

Install Fig::

    $ sudo pip install -U fig


Building and Running the Poppy API Server
-----------------------------------------

From this folder, run::

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
