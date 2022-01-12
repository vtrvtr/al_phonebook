# Overview

This program is a CLI first that allows users to register and query information about contacts. The project will be split into a library section that contains all the main logic for the program and a CLI section that uses that library to expose a user-facing interface.

The library will be written in Python primarily because of its vast ecosystem that offers a variety of third party modules. It will target Python 3.10 due to it being the most recent release and being compatible with all the necessary libraries used.

A MIT license will be used since there are no plans to monetize this project in any way.

Key features:

- The CLI should allow users to:
  - Add more contacts;
  - Remove contacts;
  - Search for a particular information;
  - List all contacts data;
  - Filter contact list based on contact data;
  - Separate contacts into groups.

Stretch features:

- Allow users to define their own contact information schemas;
- Allow users to configure how contact information is displayed.

# Developer considerations

- The project manager used will be `poetry`. An alternative `requirements.txt` will be provided to maximize compatibility in the case the user doesn't have access to `poetry`.
- The project will be fully typed and statically checked by `mypy` to increase the probability of correctness.
- The testing framework used will be `pytest` to simplify test-writting. Test coverage should be 100% for the library and at least 75% for the CLI part. 
- The project will be developed on Windows 10 and tested on the Windows Linux Subsystem to guarantee compatibility. The distro used will be Debian. 
