# mail-cleanup

# Add Docker Desktop for Mac (docker)

export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin/"

# Docker commandsopen -a Docker

```
open -a Docker #for Mac

docker login registry.gitlab.com # login is email address

docker build -t registry.gitlab.com/personal1741534/mail-cleanup/ubuntu-terraform .

docker run -it registry.gitlab.com/personal1741534/mail-cleanup/ubuntu-terraform /bin/bash

docker push registry.gitlab.com/personal1741534/mail-cleanup/ubuntu-terraform
```
