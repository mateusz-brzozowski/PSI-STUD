FROM gcc:10

RUN apt update
RUN apt install -y cmake

WORKDIR /usr/app/src

COPY . /usr/app/src

RUN cmake -S . -B ./build/
RUN cmake --build ./build/
