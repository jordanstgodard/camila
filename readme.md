# Todo
1. Update documentation
2. Implement more runtime behavior
2. Implement and test workers over proxies using --proxies
2. Design and implement modularized CNC attack classes.
# Usage
**camila** is run dynamically from command line and controlled via PRIVMSG


| Argument | Alias             | Description                                                                   |
| -------- | ----------------- | ----------------------------------------------------------------------------- |
| -a       | --attack-names    | List of initial names to attack                                               |
| -c       | --attack-channels | List of initial channels to join and attack                                   |
| -i       | --ignore-names    | List of initial names to ignore                                               |
| -p       | --proxies         | List of SOCKS5 proxies in the format SERVER:PORT                              |
| -s *     | --server          | Defines the server to attack. Must be in the format SERVER:PORT               |
| -t       | --threads         | Number of threads to use for camila. One thread is one worker. Defaults to 1. |
| -T       | --trusted_names   | List of trusted names to allow runtime control and command                    |
| -v       | --vhost           | Custom vhost                                                                  |
| --ipv6   |                   | Flag for using IPv6 sockets                                                   |
| --ssl    |                   | Flag for using SSL                                                            |