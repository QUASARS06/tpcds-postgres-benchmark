FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV PGHOST=host.docker.internal
ENV PGUSER=chiragjain

# Install system and Python dependencies
RUN apt-get update && \
    apt-get install -y build-essential cmake postgresql-client git sqlite3 bc unzip \
    byacc flex bison gcc-9 vim sudo python3 python3-pip wget && \
    apt-get install -y python3-matplotlib python3-bs4 python3-lxml python3-numpy && \
    \
    # Download and install plan-exporter
    wget https://github.com/agneum/plan-exporter/releases/download/v0.0.5/plan-exporter-0.0.5-linux-amd64.tar.gz && \
    tar -zxvf plan-exporter-0.0.5-linux-amd64.tar.gz && \
    mv plan-exporter*/plan-exporter /usr/local/bin/ && \
    rm -rf plan-exporter*

# Set working directory
WORKDIR /proj

COPY run_benchmark.sh .

# Clone the TPC-DS benchmark wrapper repo
RUN git clone https://github.com/celuk/tpcds-postgres

WORKDIR /proj/tpcds-postgres

# Clean up and copy our local scripts
RUN rm -f tpcds_generator.sh pgtpcds_defaults get_analyzed_txts.sh

COPY tpcds_generator.sh .
COPY pgtpcds_defaults .
COPY get_analyzed_txts.sh .
COPY analyze_explains_offline.py .

CMD ["/bin/bash"]
