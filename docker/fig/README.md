Install Fig::

    $ sudo pip install -U fig

Build and Run::

    $ fig up -d

To stop all your fig containers::

    $ fig stop

To start all your fig containers without rebuilding::

    $ fig start

To get the most-updated code of poppy::

    $ fig run poppy git --git-dir=/home/poppy/.git pull

