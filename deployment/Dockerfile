FROM lidauch/basechembase:latest as builder

ARG ENV_NAME

# Install MMPDB first as it's less likely to change, with edited smarts_aliases.py
COPY ./basechem/common/mmpdb_data/smarts_aliases.py /opt/mmpdb-3.1/mmpdblib/smarts_aliases.py
RUN source ~/.bashrc && \
    python -m pip install /opt/mmpdb-3.1 && \
    rm -rf /root/.cache/pip

# Install Python dependencies
COPY ./requirements/base.txt .
RUN source ~/.bashrc && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r base.txt && \
    rm -rf /root/.cache/pip

# Install npm dependencies
COPY package*.json ./
RUN source ~/.bashrc && \
    npm ci && \
    npm cache clean --force && \
    rm -rf /root/.npm

# Create app directory
ENV HOME=/home/app
ENV APP_HOME=$HOME/web
WORKDIR $APP_HOME

RUN mkdir -p $APP_HOME/log && \
    mkdir -p $APP_HOME/public/static && \
    mkdir -p $APP_HOME/public/media && \
    cp /root/.bashrc $HOME/.bashrc

# Copy deployment files
COPY ./deployment/services.$ENV_NAME.ini /etc/supervisord.d/
COPY ./deployment/entrypoint.$ENV_NAME.sh ./entrypoint.sh
COPY ./deployment/.env.$ENV_NAME ./.env

# Copy project files last (as they change most frequently)
COPY . .
RUN chmod 600 /home/app/web/deployment/.ssh/something.pem

ENTRYPOINT ["/home/app/web/entrypoint.sh"]