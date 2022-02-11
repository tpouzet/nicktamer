#! /usr/bin/env python
#
# Example program using irc.bot.
#
# Joel Rosdahl <joel@rosdahl.net>

"""A simple example bot.
This is an example bot that uses the SingleServerIRCBot class from
irc.bot.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.
The known commands are:
    stats -- Prints some channel information.
    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.
    die -- Let the bot cease to exist.
    dcc -- Let the bot invite you to a DCC CHAT connection.
"""

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

import giphy_client 
import json
from giphy_client.rest import ApiException
from pprint import pprint

import time
import random

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        #print(e)
        a = e.arguments[0].split(" ", 6)

        if a[0] == "!gif":
                self.do_command(e, a[0][1:])
        elif a[0] == "!wizz":
            self.do_command(e, a[0][1:])
        elif a[0] == "!insult":
            self.do_command(e, a[0][1:])
        elif a[0] == "!help":
            self.do_command(e, a[0][1:])
        return

    def on_dccmsg(self, c, e):
        # non-chat DCC messages are raw bytes; decode as text
        text = e.arguments[0].decode('utf-8')
        c.privmsg("You said: " + text)

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die() 	
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = sorted(chobj.users())
                c.notice(nick, "Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp(
                "DCC",
                nick,
                "CHAT chat %s %d"
                % (ip_quad_to_numstr(dcc.localaddress), dcc.localport),
            )
        elif cmd == "gif":

             search=e.arguments[0].split(" ", 6)
             del search[0]
             #print(search)
             
             api_instance = giphy_client.DefaultApi()
             api_key = 'x' # str | Giphy API Key.
             q = search # str | Search query term or prhase.
             limit = 1 # int | The maximum number of records to return. (optional) (default to 25)
             offset = 0 # int | An optional results offset. Defaults to 0. (optional) (default to 0)
             rating = 'g' # str | Filters results by specified rating. (optional)
             lang = 'fr' # str | Specify default country for regional content; use a 2-letter ISO 639-1 country code. See list of supported languages <a href = \"../language-support\">here</a>. (optional)
             fmt = 'json' # str | Used to indicate the expected response format. Default is Json. (optional) (default to json)
             
             try: 
                 api_response = api_instance.gifs_search_get(api_key, q, limit=limit, offset=offset, rating=rating, lang=lang, fmt=fmt)
                 #print(api_response)
             except ApiException as e:
                 print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)

             api_response_dictionary = api_response.to_dict()

             c.privmsg("#entiteparfaite",api_response_dictionary["data"][0]["images"]["downsized_large"]["url"])

        elif cmd == "wizz":
             victim=e.arguments[0].split(" ", 2)
             del victim[0]
             
             for x in range(60):
                 #print(victim)
                 c.privmsg("#entiteparfaite","Hey, "+victim[0]+", DU NERF ESPECE DE GLANDEUR !!!!!!!!")
                 time.sleep(1)
                
        elif cmd == "insult":
             c.privmsg("#entiteparfaite",random.choice(list(open('insults.txt'))).strip())

        elif cmd == "help":
             c.privmsg("#entiteparfaite","!gif + <up to 5 keywords> = gif link")
             c.privmsg("#entiteparfaite","!wizz + <nickname> = annoys everyone")
             c.privmsg("#entiteparfaite","!insult = gives you a roast")

        else:
            c.notice(nick, "Not understood: " + cmd)


def main():
    import sys

    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = TestBot(channel, nickname, server, port)
    bot.start()


if __name__ == "__main__":
    main()
