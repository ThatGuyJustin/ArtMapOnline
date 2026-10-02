# ArtMapOnline

> Did this need to be a full stack app?

No.

> Then why?

Well, the other alternative was a cloudflare worker, and I refuse to let Nadie win.

This is a webapp to convert images to Minecraft maps, with proper scaling, and then for use with the [ArtMap](https://gitlab.com/BlockStack/ArtMap) plugin

ToDo:
1) Docker build
2) Cleanup the images
3) Timed tasks to clean out memory cache, or just figure out a better cache in general.

# Example Docker file
`docker/compose.example.yml`

# Live enviroment
`docker compose -f docker/compose.live.yml up --build`
`docker compose -f docker/compose.live.yml down --rmi all`