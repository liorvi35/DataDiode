# Data Diode

Data-Diode is an architecture (conception) where the data flow is unidirectional (not including the acknowledgments or other signals, for reliable communication). The data firstly flows from a sender which sends the data into the system to a first proxy server, data is being sent using TCP (Transmission Control Protocol) socket. After data is received by first proxy, it is being sent to a second proxy server but now using a RUDP (Reliable User Datagram Protocol, our implementation), the meaning is that if the first proxy will be attacked and captured, the attacker could not continue capturing data because he doesnt know how our's RUDP works. Then, finally, the data is being send from the second proxy to an end-user, receiver, using TCP.<br/>In our implementation we are sending a file and in each step in system's data flow, file's data is being transferred only in one direction<br/>(Sender->Proxy1->Proxy2->Receiver), of course except of acknowledgments.<br/>Architecture of a Data-Diode is a sort of one-sided firewall, what can improve the security of incoming data.

## Requirements
Before using the Diode program, make sure your system meets the following requirements:
-   Python version 3.
-   Debian-based system.
-   Docker.

## Building and Installing 🏗️
You can install the Diode program by following these steps:

1.  Clone this repository to your local machine using the following command:<br/>`git clone https://github.com/liorvi35/DataDiode.git`.
    
2.  Install the required modules by running the following command:<br/>`pip3 install -r requirements.txt`.
    
3.  Install Docker by running the following command:<br/>`sudo snap install docker`.

4.  Set up the Docker container's by using:<br/>`docker-compose up` on the `compose-docker.yml` file.

## Usage
To use the Diode program, you need to run all python scripts from a Docker containers:
1.  Open a terminal and run:<br/>`sudo su` and then `docker ps`

2. Open 4 other teminals in each run:<br/>`sudo su` and then `docker exec -it <ID> /bin/bash`, when you should replace `<ID>` with the right identifier from the `ps` command.

3.  Then in right order you should load the python scripts:<br/>`Sender.py`, `Proxy1.py`, `Proxy2.py`, `Receiver.py`.

4.  After loading in each container the scripts, you can run each program by:<br/>`python3 Sender.py <file>`, where `<file>` is a valid path to file that should be sent.<br/>`python3 Proxy1.py`.<br/>`python3 Proxy2.py`.<br/>`python3 Receiver.py`.


## Skills 🔧
- Python programming.
- Version control with Git & Github.
- Socket programming in TCP, UDP, Reliable-UDP.
- Computers-Communication knowledge.
