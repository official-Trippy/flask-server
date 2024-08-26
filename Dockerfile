# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies required for MeCab
RUN apt-get update && apt-get install -y \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    curl \
    xz-utils \
    git \
    build-essential \
    && apt-get clean

# Install mecab-python3
RUN pip install mecab-python3

# Clone and install mecab-ko and mecab-ko-dic
RUN git clone https://bitbucket.org/eunjeon/mecab-ko.git /tmp/mecab-ko \
    && cd /tmp/mecab-ko \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install

RUN git clone https://bitbucket.org/eunjeon/mecab-ko-dic.git /tmp/mecab-ko-dic \
    && cd /tmp/mecab-ko-dic \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install

# Ensure MeCab finds the correct mecabrc and dictionary
RUN ln -s /usr/local/etc/mecabrc /etc/mecabrc

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 (or any other port your Flask app is running on)
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "5000"]
