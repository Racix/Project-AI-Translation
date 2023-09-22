# Project-AI-Translation

## Friday - 2023-09-22
The first two weeks of working with the project we have divided the project into three parts and from that each sub group studied the topic further and decided which architectures would be used their part. The goal for the first sprint, ending 2023-09-29, is to have a back end up and running with two models that can produce some kind of output, the quality is not that important yet. The project have the following parts:

### Backend
[@IsakLundstrom](https://github.com/IsakLundstrom), [@Racix](https://www.github.com/Racix), [Lundsak](https://github.com/Lundsak)

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
