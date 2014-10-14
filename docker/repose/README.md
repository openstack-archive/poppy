Based on the Repose Wiki Instructions: https://repose.atlassian.net/wiki/display/REPOSE/Docker


Building the Repose Docker Image
--------------------------------------

From the docker/repose folder:

    $ docker build -t repose_img_1 .




Running the Repose Docker Container
--------------------------------------

Name the container 'repose'

    $ docker run -d -p 80:80 --name repose repose_img_1 


