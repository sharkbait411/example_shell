# pull base Docker image
# In this specific infrastructure case, the python:3.10.1-slim image is used by default. This can be updated as needed,
#   including using the standard development tag: 'latest'. We use a specific image here, for production considerations,
#   it is a smart idea to treat your development as if its production in order to streamline your development to prod
#   work flows. This also allows us to standardize the setup process for all shells, as well as document and
#   individualize each shell in a documented fashion... for transparency, and validation
FROM python:3.10.1-slim

# next step is to make the shell directory in the container, copy the shell into the container,
#   and make the working directory the shell location
RUN mkdir -p /usr/local/app
COPY . /usr/local/app
WORKDIR /usr/local/app

## Single run for reducing build container images
## add optional updating of sources, and certs if needed
# lines to add:
#   && sed -i -e 's/deb.debian.org/ex.artifactory.server.com/g' -e 's/security.debian.org/ex.artifactory.server.com/g' /etc/apt/sources.list \
#   && curl -k http://ex.artifactory.server.com/bootstrap/pki/scripts/debian-certs.sh -o /tmp/debian-certs.sh \
#   && bash /tmp/debian-certs.sh \
#   && rm -f /tmp/debian-certs.sh \
#   && python3 -m pip config set global.index-url https://ex.artifactory.server.com/artifactory/api/pypi/releng-pypi/simple \
#   && python3 -m pip config set global.cert /etc/ssl/certs \
#
## otherwise use the standard docker run setup below
## updating ssl permissions (the debian base in python, has ssl set to high, so we lower it back down)
## updating python pypi and specific packages
RUN apt-get update -y \
 && apt-get install -y openssl iputils-ping dnsutils \
 && sed -i -e '/^MinProtocol/s/=.*/= None/g' -e '/^CipherString/s/=.*/= DEFAULT/g' /etc/ssl/openssl.cnf \
 && python3 -m pip install --upgrade pip \
 && python3 -m pip install --upgrade setuptools \
 && python3 -m pip install --upgrade wheel \
 && python3 -m pip install --no-cache-dir -r /usr/local/app/requirements.txt

# run python shell - this will automatically run your shell. Alternatively, if you wish write your dockerfile, to build,
#  then run 'docker run -it --name <name of your container> <docker image:docker-tag> /bin/bash' to enter the container
#  built from your newly built email, and then you can simply run 'python <file> <options - if any>'
#    - simply comment out the below line.
CMD ["python", "/usr/local/app/example/main.py"]
