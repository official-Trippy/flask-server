# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies required for MeCab and general tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-utils \
    tzdata \
    g++ \
    git \
    curl \
    software-properties-common \
    default-jdk \
    default-jre \
    automake \
    autoconf \
    make \
    sudo \
    && apt-get clean

# Install MeCab
RUN cd /tmp && \
    curl -LO https://bitbucket.org/eunjeon/mecab-ko/downloads/mecab-0.996-ko-0.9.1.tar.gz && \
    tar zxfv mecab-0.996-ko-0.9.1.tar.gz && \
    cd mecab-0.996-ko-0.9.1 && \
    ./configure && \
    make && \
    make check && \
    sudo make install

# Install mecab-ko-dic
RUN cd /tmp && \
    curl -LO https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.0.1-20150920.tar.gz && \
    tar -zxvf mecab-ko-dic-2.0.1-20150920.tar.gz && \
    cd mecab-ko-dic-2.0.1-20150920 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    sudo sh -c 'echo "dicdir=/usr/local/lib/mecab/dic/mecab-ko-dic" > /usr/local/etc/mecabrc' && \
    sudo make install

# Install mecab-python
RUN cd /tmp && \
    git clone https://bitbucket.org/eunjeon/mecab-python-0.996.git && \
    cd mecab-python-0.996 && \
    python3 setup.py build && \
    python3 setup.py install

# Set the locale environment variables
ENV LANG=C.UTF-8
ENV LANGUAGE=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the Flask application
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "5000"]
