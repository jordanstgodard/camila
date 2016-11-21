# Todo
1. Update documentation
2. Implement more runtime behavior
2. Implement and test workers over proxies using --proxies
2. Design and implement modularized CNC attack classes.



-----


# Usage
**camila** is run dynamically from command line and controlled via PRIVMSG


| Argument | Alias             | Description                                                                                      |
| -------- | ----------------- | ------------------------------------------------------------------------------------------------ |
| -a       | --attack-names    | List of initial names to attack. Note, when this is set nicks from joined channels are NOT added |
| -c       | --attack-channels | List of initial channels to join and attack                                                      |
| -i       | --ignore-names    | List of initial names to ignore                                                                  |
| -p       | --proxies         | List of SOCKS5 proxies in the format SERVER:PORT                                                 |
| -s *     | --server          | Defines the server to attack. Must be in the format SERVER:PORT                                  |
| -t       | --threads         | Number of threads to use for camila. One thread is one worker. Defaults to 1.                    |
| -T *     | --trusted_names   | List of trusted names to allow runtime control and command                                       |
| -v       | --vhost           | Custom vhost                                                                                     |
| --ipv6   |                   | Flag for using IPv6 sockets                                                                      |
| --ssl    |                   | Flag for using SSL                                                                               |

A star * denotes required field

Example usage:
`python camila.py --server irc.myserver.com:6667 -c "#server-help" "#server-home" -T sapphire -a mark jim bob -i sapphire john -t 100`
Runs camila.py with 100 threads on irc.myserver.com:6667 with
* "#server-help" and "#server-home" as autojoined attack channels
* sapphire as a trusted name
* mark, jim, and bob as attack names
* sapphire and john as ignore namee
Thus, this would NOT start attacking. It would only define the channels to autojoin and the preset nicks to attack, ignore, and trust.