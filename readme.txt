Text-based Multi-user Fantasy RPG
---------------------------------

This project was started just to try out ZeroMQ!

At present, there is a curses client and a server program.

Users can enter text (speech!) that will be displayed on the client of other
users in the same virtual location.

Commands can be entered using a /verb notation.

Currently recognized commands are:

 /go <location name>	- change location 
 /look - get description of current location
 /attack - begin combat against an enemy
 /map - display an onscreen map
 /search - look for treasure in current location
 /loot - look for valuables on a deceased adversary


Any text that doesn't begin with '/' will be interpreted as speech and sent to
all other users in the same room.

There is a basic random room generator which builds simple descriptions for
previously unknown locations, along with a random Orc.

Technical details
-----------------

The client uses two ZeroMQ socket connections to the server:

1) A SUB socket that receives multi-cast notifications from the server and from
other users.  Two subscriptions are maintained: a location-specific subscription
and a player-specific subscription.

Player speech events are sent with the location-specific subscription 
Player combat events are sent on the player-specific subscription channel.

2) A REQ/REP socket which carries user requests to the server and server responses.

Both the client and server run an event loop based on ZeroMQ's event poller.

The REQ/REP socket will receive objects of two types from the client:

Event objects - used by the client to update the server's state
		The server will typically respond "OK", or send back updated
		information.

Request objects - instructions from the user
		The server will send back a response which contains the results
		of the user's action


Features to implement
---------------------

* Magic!
* Potions
* Experience points
* Inventory
* Keys/Locks
* Location discovery (based on dungeons made of interconnecting rooms)
* Dungeon authoring tools (possibly web-based with SVG maps).
* Server side persistance (all state is in-memory at present)
* Player unconsciousness/death
* Protocol negotiation/versioning

TODO
----

At present, some location-state is kept in the client.  In the future it is
intended that the server will hold all state.

It is planned that instructions which take one-or-more parameters will support
basic tab-completion using a completion dialog.  This has already been partially
implemented with the /go command, which offers the four compass directions as
completion options.

System requirements:
--------------------

Python bindings for the ZeroMQ library (apt-get install python-zmq on
Debian/Ubuntu)

Running the client
------------------

Open two terminals.  In one terminal, change directory to the checkout and run:

 python server.py

In the other terminal, change directory to the checkout and run:

 python client.py

By default, the client will connect to the server on localhost:5555 and
localhost:5557.

You can run additional clients with "python client.py -u <username>".

Config file
-----------

client.cfg is a standard ini-file which contains settings for the default
username (where no '-u' parameter has been passed) and a set of keyboard macros.

Final Notes
-----------

Some of the components have been hastily assembled starting with a single-file
script which later had bits moved out to modules.  None of this is CV-quality
code (yet)!

