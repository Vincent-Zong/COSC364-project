# COSC364-project
The archive of COSC364 Routing Information Protocol.
---
This project implments a "routing daemon" as a normal userspace program under Linux.
Instead of sending its routing packets over real network interfaces, the routing daemon will communicate with its peer daemons (which run in parallel on the same machine) through local sockets.
---
## Running the project locally
1. Clone the repository code from GitHub to local machine
   Clone with HTTPS: `git clone https://github.com/Vincent-Zong/COSC364-project.git`
2. Start a terminal from the project directory
3. Enter command with configuration file router1`python3 daemon.py configuration_files/router1.ini`.
4. The terminal will print routing tables.
5. Start separate terminals and enter commands following the same pattern for rest of configuration files.
6. If all daemons are set up correctly, the network of routers will be the same as figure 1 of assignment description.
7. Adding or removing running daemons will cause routing tables automatically updating based on the current network.
