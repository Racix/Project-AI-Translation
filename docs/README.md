# Weekly blog

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
