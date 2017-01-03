# Tournament

This Python application provides a list of items within a variety of categories, as well as a user registration and authentication system.

## Installation

1. Download and install the base [VirtualBox platform package](https://www.virtualbox.org/wiki/Downloads).

2. Download and install [Vagrant](https://www.vagrantup.com/downloads.html).

3. Fork this repo, change into the project's directory, and start up the virtual machine by typing the following into the command line. Note that this could take several minutes.

```
$ vagrant up
```

4. Log into the virtual machine by typing the following into the command line:

```
$ vagrant ssh
```

5. Change to the following directory by typing in the command line:

```
vagrant@vagrant-ubuntu-trusty-32:~$ cd /vagrant/catalog
```

6. Start the server by typing the following in the command line:

```
vagrant@vagrant-ubuntu-trusty-32:/vagrant/catalog$ python catalog_webserver.py
```

## License

The application is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).