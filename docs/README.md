# Weekly blog

## Tuesday - 2023-12-12
We are entering our final phase of our development and adding our finishing touches. Most parts are now up and running on the Google Kubernetes enginge.

Our final demo will be presented live on zoom in exactly a week from when this was written! For more info see the webpage for [Luleå University of Technology](https://www.ltu.se/org/srt/Redovisning-av-projektkurs-fagelskadning-P-skivor-och-AI-1.234385?l=en)

## Friday - 2023-12-01
Weekly update, we are now able to deploy everything to Google Kubernetes Engine using their compute power, have not yet deployed live transcription and translation service to the cluster, the other serivces are deployed and mostly working with some minor bugs. As for the other services we are making progress in alot of areas and we got some pull requests that are in review and that should be merged soon.


## Friday - 2023-11-24
Weekly update, we have made some progress for several parts of our project.

**Live transcription:** </br>
Live transcription service works now with minor bugs, websockets closing randomly. Have yet to be integrated with the frontend, should be done next week.

**Translation:** </br>
The translation service have been reviewed and merged into main. Some changes were made, changed to argos translate instead to translate the whole text instead of sentences to capture context. Work for integrating this to the frontend have been made.

**Kubernetes:** </br>
We have managed to deploy our services onto a local kubernetes cluster using docker-desktop and helm. Possibly might be able to deploy it onto the rise ice kubernetes cluster next week to run our services.

## Friday - 2023-11-17
During the past three weeks we have created a microservice out of the translation and we are working on making a summary-of-transcriptions functionallity into a microservice using the language model LLaMA.
We have also been working on live-transcription and now have a first version working prototype. We have also been working on implementing a language detection for the whisper model that can handle bigger audio input. 

## Friday - 2023-10-27

During the past two weeks, most of our time has been dedicated to presentations and exams. Nevertheless, progress has been made.

On the backend, we have implemented the new, more microservices-oriented architecture we decided on earlier.

The frontend can now receive responses from the backend via websockets.

Translation functionality should now be operational. Next, we need to transform it into a dedicated translation microservice.

## Friday - 2023-10-13
This week, we have decided to make some changes to the system architecture. We are now transitioning to a more efficient microservice architecture, which will make the system more decoupled and easier to understand. Additionally, we have made progress in integrating the diarization service into the entire system.

For the frontend part, work has been put in to ensure that it can call all the currently available API routes.

We have also dedicated time to exploring video pipelining and segmentation. This will prove valuable in handling large videos and addressing potential challenges in live transcription.


## Sunday - 2023-10-08
We in the backend team decided to try and split up the model with the api gate way to enable the models to be ran on different machines if necceary and try and allow for load balancing later on. To handle errors while transcribing and diarizing we implemented a websocket server in the api gateway which the models service send status data to which can be used in the frontend. 

The frontend has been started on using React. We have a simple working example for requesting data from the server but it is not integrated yet to work with all function in the backend. 

The diarization team and the backend team will meet on monday to integrate the NeMo model with the rest of the backend.

## Friday - 2023-09-29
This week has been great but not without challenges. We have implemented a first draft of a backend API using FastAPI with routes to upload a video, save it locally and its information in a MongoDB database. We launch these using docker-compose and two Dockerfiles to make them run in seperate docker containers. Later in the week we started integrating the trascribing model to the backend using FasterWhisper with the large-v2 model. We realized that laptops might not be able to run this so currently we are using our private stationary computer to delevop the backend further (we are currently looking at how we might be able to host and develop on a cluster instead). The diarization have made good progress as well where they have explored combining the result from the whisper model with the result of thier NeMo model to classify the different spekers of a recording. We will (if things go as planned) try and integrate their result to the backend next week.

## Friday - 2023-09-22
The first two weeks of working with the project we have divided the project into three parts and from that each sub group studied the topic further and decided which architectures would be used their part. The goal for the first sprint, ending 2023-09-29, is to have a back end up and running with two models that can produce some kind of output, the quality is not that important yet. The project have the following parts:

### Backend
[@IsakLundstrom](https://github.com/IsakLundstrom), [@Racix](https://www.github.com/Racix), [@Lundsak](https://github.com/Lundsak)

The current state of the backend: 
* REST API - [@Fast API](https://fastapi.tiangolo.com/) (Python)
* Database - MongoDB or Cassandra
* Streaming - Not yet decided.
  
### Transcription model
[@ClaudeHallard](https://github.com/ClaudeHallard), [@hamidehsani54](https://github.com/hamidehsani54)

The whisper model will be used for transcribing the audio/video files and the following Whisper implementations have been tested:
* [@WhisperJAX](https://github.com/sanchit-gandhi/whisper-jax)
* [@faster_whisper](https://github.com/guillaumekln/faster-whisper)
  
### Diarization model
[@oskar-dah](https://github.com/oskar-dah), [@langemittbacken](https://github.com/langemittbacken), [@tonytonfisk2](https://github.com/tonytonfisk2)

For determening who is speaking two diarization models have been tested, pyannote was easy to set up but did not perform vey well so we decided to also test the NeMo model which we have not yet been able to test since it has been more difficult to get it to run. 
* [@NeMo](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/stable/asr/speaker_diarization/intro.html)
* [@pyannote](https://github.com/pyannote/pyannote-audio)
