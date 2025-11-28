# COSC364-project
The archive of COSC364 Routing Information Protocol.
---
This project implments a "routing daemon" as a normal userspace program under Linux.
Instead of sending its routing packets over real network interfaces, the routing daemon will communicate with its peer daemons (which run in parallel on the same machine) through local sockets.
## Running the project locally
1. Clone the repository code from GitHub to local machine
   Clone with HTTPS: `git clone https://github.com/Vincent-Zong/COSC364-project.git`
2. Start a terminal from the project directory
3. Enter command `python3`
