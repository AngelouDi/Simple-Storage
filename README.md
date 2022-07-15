## Simple Storage
---
**Simple Storage** is a simple, free, clean and lightweight storage management system that helps you and your team manage your inventory built on python Flask.

**Users** can claim items from **Warehouses** and everyone can find where everything is at any moment easily. 

![Tutorial][tutorial]

## Features
---
- Login System
- Claiming and Returning of items
- Item searching
- Item editing
- Creating and managing warehouses
- Everything stored in postgres database

## Privacy and Security
---
**Simple Storage** doesn't log any user data except the account information. No requests are made to any 3rd party services, and only a single session cookie is used so users can't be tracked.


Passwords are stored as **Bcrypt** hashes.

## Deployment
---
Dockerfile and docker-compose is provided, just run `docker compose up` and you are up and running on port 80.
> **Warning**
> You should first change your *flask key* and *database key* inside the .env file.

## Baby steps
---

> **Warning**
> **Simple Storage** Is still in the very early stages of production. There **exist** bugs, unfinished/unpolished UI and possible backend security problems (these don't include user infromation and credentials).

## TODO:
---
- [ ] Invitation system so only invited people can join
- [ ] Admin panel
- [ ] User separation in users/admins
- [ ] Email verification 
- [ ] Better UI/UX
- [ ] Improve Security
- [ ] Refactor code for better maintability and readability

[tutorial]: resources/overview.webp
