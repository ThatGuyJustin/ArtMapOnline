![Minecraft Map Image](/frontend/public/assets/img/map_texture.webp)
# ArtMapOnline

> [!NOTE]
> One point of this project is to help me learn frontend development. So parts of this will more than likely be AI assisted. As I learn new concepts and proper technique, code will be migrated from slop/vibe to structured and better written.

# What is this project?
This is a *almost* full stack application that takes any image and converts it to a scaled output using Minecraft's map colors. It then provides a detailed legend that when combined with the [ArtMap](https://gitlab.com/BlockStack/ArtMap) plugin, can be used to draw that map in game.

## The Stack
* **Frontend**: 
  * Language: Node.js
  * Framework: [React](https://react.dev/) (Using [react-router](https://reactrouter.com/home))
* **Backend**:
  * Language: Python
  * Framework: [Flask](https://flask.palletsprojects.com/en/stable/)
* **Database**:
  * Redis `TODO`

## ToDo
- [x] Docker build
- [x] Cleanup the images 
- [ ] Move to redis cache
- [ ] Allow for setting changes in the frontend
  - Canvas size, dithering change etc.


## Running
When building, it builds the frontend into an [SPA](https://developer.mozilla.org/en-US/docs/Glossary/SPA), which is then served by flask.

### Production
#### Docker Compose
You can use the compose file
> docker/compose.example.yml
#### Docker Run
> `docker container run -p 8000:8000 ghcr.io/thatguyjustin/artmaponline:latest`

### Development
#### Docker Compose

Spin up the environment
> `docker compose -f docker/compose.live.yml up --build`

Post-development Cleanup
> `docker compose -f docker/compose.live.yml down --rmi all`
