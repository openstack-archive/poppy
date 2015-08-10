Building the E2E Test Site Image
--------------------------------

From the docker/e2e_test folder:

    $ docker build -t e2e_flasksite_1 .


Running the E2E Test Site Docker Container
------------------------------------------

Name the container 'e2e_flasksite':

    $ docker run -d -p 80:80 --name e2e_flasksite e2e_flasksite_1

