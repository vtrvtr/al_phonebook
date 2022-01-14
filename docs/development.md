# Overview

In this document we'll chronicle the architectural decisions made throughout the project. The order of entries is merely chronological.


# Entries

## Overall first impression

The project seems relatively simple at first glance. I chose to use Python instead of C++ simply because there are more libraries readily available. A worry that I have with Python is that using the project is harder than it would be compared to a simply statically linked binary. I plan to mitigate this issue by providing a one-stop-script that should setup the project completely. I'll be using `poetry` for package management just because it's my favorite one. I'll provide a vanilla, pip compliant `requirements.txt` in case the user doesn't want to use `poetry`.

I will use sqlite for the backend and SQLModel for the schemas. Probably use `textual` for the cli. 


## SQL 

At first I thought using SQL would be natural since we would need to filter, add, remove etc. However, the fact that one of the requirements is to be able to extend the default schema made me change my mind. Although it's possible to create a SQL DB with dynamic schema, IMO it isn't worth it for this project given. It's also not the focus of the technology. Instead, I thought to use Mongo, but then it stroke me that Mongo is basically a superpowered dictionary. So I'll start the implementation with good'n'old json. Performance wise this is also fine since we'll be able to read the whole database in memory and it's unlikely anyone would have enough contacts that would make the process slow. 

Models can be described using pydantic and dynamically changed if needed. 


## TinyDB

TinyDB is a little NoSQL database written in a less than 2k lines of code which works perfectly for this small project. I will, however, abstract the database so it's easy to change to another one if necessary.

