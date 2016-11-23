# Todo
1. Update documentation
2. Implement more runtime behavior
3. Implement and test nodes over proxies using --proxies
4. Design and implement modularized CNC attack classes. This works with camila --attack [module name] and camila --stop [module name]


-----


# Usage
**camila** is run dynamically from command line and controlled via PRIVMSG to any nodes. Initial execution does allow for some parameterization as shown below.


| Argument | Alias             | Description                                                                                      |
| -------- | ----------------- | ------------------------------------------------------------------------------------------------ |
| -a       | --attack-names    | List of initial names to attack. Note, when this is set nicks from joined channels are NOT added |
| -c       | --attack-channels | List of initial channels to join and attack                                                      |
| -i       | --ignore-names    | List of initial names to ignore                                                                  |
| -p       | --proxies         | List of SOCKS5 proxies in the format SERVER:PORT                                                 |
| -s *     | --server          | Defines the server to attack. Must be in the format SERVER:PORT                                  |
| -t       | --threads         | Number of threads to use for camila. One thread is one node. Defaults to 1.                      |
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

At runtime, **camila** is controlled via PRIVMSG. Any node may be privately messaged by a trusted user with the following commands.
Each of these commands must be preceeded by the word **camila**.


| Argument | Properties                                    | Description                                        |
| -------- | --------------------------------------------- | -------------------------------------------------- |
| -a       | [add, remove, list]                           | Add, remove, or list attack names                  |
| -c       | [add, remove, list]                           | Add, remove, or list attack channels               |
| -i       | [add, remove, list]                           | Add, remove, or list ignore names                  |
| -k       | [name1, name2,... nameN] or empty to kill all | Kill a list of workers or all if property is empty |
| -s       |                                               | List the status.                                   |
| -T       | [add, remove, list]                           | Add, remove, or list trusted names                 |

Example usage:
`/PRIVMSG camila camila -a list`
Will private message a nick, camila, with the command `camila -a list` to list all attack names.

Example usage:
`/PRIVMSG camila camila -T add sapphire franklin jimmy`
Will private message a nick, camila, with the command `camila -T add sapphire franklin jimmy` to add the list of names as trusted names.

Note, only trusted names are able to run these commands. A non-trusted user may still message any camila node but will not be able to execute any commands. For this reason, one or more trusted names should be specified during execution time.

Note, one can message any node in camila to execute these commands.