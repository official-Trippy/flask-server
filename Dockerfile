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
    automake \
    autoconf \
    && apt-get clean

# Clone and install mecab-ko
RUN git clone https://bitbucket.org/eunjeon/mecab-ko.git /tmp/mecab-ko \
    && cd /tmp/mecab-ko \
    && ./configure \
    && make \
    && make install

# Clone and install mecab-ko-dic using the install.sh script
RUN git clone https://bitbucket.org/eunjeon/mecab-ko-dic.git /tmp/mecab-ko-dic \
    && cd /tmp/mecab-ko-dic \
    && ./install.sh

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
