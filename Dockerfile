FROM debian:stretch

RUN apt update
RUN apt -y -qq install openjdk-8-jdk python3 python3-pip git wget uuid-runtime gradle

ARG INSTALL_PATH=/tmp/rundeck_install
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

ARG RUNDECK_DEB=rundeck_3.2.8.20200608-1_all.deb
RUN wget https://dl.bintray.com/rundeck/rundeck-deb/$RUNDECK_DEB
RUN dpkg -i $RUNDECK_DEB && rm $RUNDECK_DEB

COPY ./ .
RUN pip3 install -r requirements.txt

WORKDIR src/
RUN gradle wrapper # TODO where?
RUN python3 build.py

# tail null so the container doesn't stop after Rundeck service is started
CMD /etc/init.d/rundeckd start && tail -f /dev/null
