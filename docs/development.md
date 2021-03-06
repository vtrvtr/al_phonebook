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

## Delete functionality

Delete functionality is actually not in the prompt for the task. I was going to implement it, but I'll skip since it was not asked for. 


# Further work

* Clarify what "display information in at least 2 ways" mean. I didn't have enough time to implement it, but `rich` offers lots of customization for how to display the text in the terminal. Anyway, my plan was to write a `Printer` class that would have a `formatter` argument, which in turn would translate an `Item` to some kind of formatting. If the task was to implement different kinds of text styles, `formatter` could do that exposing a subset of `rich`s styling capabilities. If it would be more of a layout question, e.g how many fields to display, then maybe isolate that part into an object that would take an `Item` and return only the fields specified by the user.
