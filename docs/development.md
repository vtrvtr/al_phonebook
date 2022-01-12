# Overview

In this document we'll chronicle the archtectural decisions made throughout the project. The order of entries is merely chronological.


# Entries

## Overall first impression

The project seems relatively simple at first glance. I chose to use Python instead of C++ simply because there are more libraries readily available. A worry that I have with Python is that using the project is harder than it would be compared to a simply statically linked binary. I plan to mitigate this issue by providing a one-stop-script that should setup the project completely. I'll be using `poetry` for package management just because it's my favorite one. I'll provide a vanilla, pip compliant `requirements.txt` in case the user doesn't want to use `poetry`.

I will use sqlite for the backend and SQLModel for the schemas. Probably use `textual` for the cli. 


