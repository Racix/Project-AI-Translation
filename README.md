# DoRiS - Diarization of Recordings in Speech-to-text

Today, there is a pressing need for speech transcription and translation to increase the accessibility of information for everyone in society. This need comes in various forms such as live meetings, recorded videos, or phone calls. Therefore, we are developing a service that, with the help of AI, can automate these processes to efficiently use time and resources.

We are a group of 8 students from Luleå University of Technology in Sweden that has developed this work during a project course on the Master Programme in Computer Science and Engineering, with specialisation Information and Communication Technology. Our work combines some more or less well-known AI tools for Transcribtion, Diarization, Translation and text summarization.

**Our models used**

On top of our backend we have developed a frontend using React.js that uses api calls to exchange audio files and trancsription results with the backend

TODO

TODO

TODO

TODO

some models can only run with a cuda compatible GPU, standard in this project is to run on cpu. To run with GPU, go to the backend.sh script and change **COMPOSE_FILE="compose.yaml"** into COMPOSE_FILE="compose-gpu.yaml" and make eventual necessary changes to the .yaml file to make it run with your gpu.

To run the start script you need to first install the docker engine. One way of doing that is by installing [Docker Desktop](https://www.docker.com/products/docker-desktop/).

When you have docker engine installed, run **./start.sh** to build the backend and frontend. You can also build them seperately by going to their respective folders and run the **backend.sh** and/or the **frontend.sh** scripts.
