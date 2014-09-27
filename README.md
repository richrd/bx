# bx

Modular Python IRC bot made from scratch.

Come and talk to me at #bxbot @ QuakeNet :)

## Features
* 40+ modules with general features including:
  * Authentication with different userlevels
  * Auto op for trusted users
  * Leave a message to an offline user
  * Broadcast text or command output on to channels periodicly
  * Channel logs, and log searching
  * Higlight command to higlight everyone on a channel
  * Channel mode enforcing
  * Join and part commands
  * Will answer simple questins
  * Nick changer
  * Calculator
  * Link title paster
  * 'wtf' for looking up acronyms
* Integrated help available
* Supports user accounts and access control
* Simple to extend if you know Python
* Aims to be compatible with Symbian S60 for hosting a bot on a phone :)
  * Comming later: module for shooting and uploading pictures from a phone

## To-do

### Documentation
* More comments
* General docs
* Module API reference

### Features
* Core
  * Implement broadcast channels, for sending out notifications
  * Make console output sane and readable
  * Implement ignoring users that haven't authed
  * Better config grouping
  * Multi server support?
  * Data store for modules
* Modules
  * Change module level
  * Change user level
  * Bot host status information
  * Command for taking photos and uploading them to a server
  * Ignore and unignore users
  * Add github commit notifier
  * Weather
* PyS60-specific functionality

### Protocol
* Implement hooks for
  * 042 RPL_YOURID
  * 265 RPL_LOCALUSERS
  * 266 RPL_GLOBALUSERS


## Module List
*   addaccount
    > Create a new account.
    > Usage: addaccount username password password

*   addchan
    > Add a channel to the autojoin list.

*   alias
    > Defines a new command alias.
    > Usage: alias new_name command

*   auth
    > Identify yourself with the bot (login). Only works via private messages.
    > Usage: auth username password

*   autochanmode
    > Automatically manage channel modes according to config.

*   autoop
    > Automatically give OP to authed users.

*   calc
    > Calculate math and python expressions. e.g. calc 3+4*6

*   clearlogs
    > Clear n. number of messages from window logs (or all if no arguments given).

*   cmds
    > Lists the commands you can use.

*   deauth
    > Logout of the bot.

*   define
    > Define terms and words related to the bot.

*   delchan
    > Remove a channel from the autojoin list.

*   deop
    > Take OPs from a nick.

*   die
    > Kill the bot.

*   dropsend
    > Clear the outgoing message buffer. Warning: removes all data queued for sending to the IRC server.

*   evl
    > Evaluate a python expression.

*   exc
    > Execute python code.

*   gainop
    > Have the bot request OPs from QuakeNet (if channel has no OPs).

*   githubnotif
    > Sends notification of new github commits to all channels.

*   help
    > Provide basic instructions on using the bot.
    > Usage: help [module]

*   highlight
    > Highlight everyone on the current channel.

*   join
    > Join list of channels, or rejoin the current channel if no channels are given.

*   kick
    > Kick a user off a channel.
    > Usage: kick [#channel] nick

*   logs
    > Print channel logs. Set time with e.g. 1h or 10m. Search logs with ?query (parameter starting with ?). Example: logs 2h ?hello

*   lvl
    > View your permission level (or someone elses).

*   mod
    > Enable or disable modules (commands & listeners).
    > Usage: mod [-/+]module_name
    > e.g. prefix module name with - or + for disable or enable

*   msg
    > Send a message as the bot to a user or channel.

*   msgcount
    > Show the message log size of the current window.

*   newpass
    > Change your password.
    > Usage: newpass oldpassword newpassword newpassword

*   nick
    > Change the nick of the bot.

*   op
    > Give OPs to yourself (default), or a list of nicks, or everyone (with '*').

*   part
    > Part list of channels.

*   ping
    > Ping the bot, to make sure it's alive and kicking.

*   qauth
    > Automatically auth with Q @ QuakeNet when connecting to IRC.

*   raw
    > Send raw data to the irc server.

*   recon
    > Reload bot config.

*   remod
    > Reload bot modules.

*   runas
    > Run a command as another user.

*   storeconf
    > Store configuration.

*   tell
    > Send a message to a user when they come online.
    > Usage: tell nick message

*   topic
    > Change the channel topic. To add to the current topic, start your topic with a '+' symbol.

*   trustme
    > Remember your account. Connects your current hostname to your account so you don't have to auth every time you connect.

*   unknowncmd
    > Intercept unknown commands and try to respond. Experimental!

*   url
    > Find links in messages and post link titles when found.

*   userinfo
    > View info about you or another nick.

*   view
    > View various bot information.

*   wtf
    > Show definitions for common acronyms.
    > Usage: wtf acronym

