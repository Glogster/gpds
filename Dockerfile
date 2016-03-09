FROM centos:centos7

RUN yum update -y && yum install -y file python-devel python-setuptools && \
    yum clean all

RUN useradd -U -s /bin/bash -u 4321 gpds

ADD . /gpds

ADD run_gpds.sh /usr/local/bin/run_gpds

WORKDIR /gpds

RUN python ./setup.py install && rm -rf /gpds

RUN mkdir -p /data/gpds && chown -R gpds:gpds /data/gpds

VOLUME /data/gpds

USER gpds

WORKDIR /data/gpds

ENV WORKERS 2

EXPOSE 8000

CMD ["run_gpds"]

