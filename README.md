# DoRiS - Diarization of Recordings in Speech-to-text

Today, there is a pressing need for speech transcription and translation to increase the accessibility of information for everyone in society. This need comes in various forms such as live meetings, recorded videos, or phone calls. Therefore, we are developing a service that, with the help of AI, can automate these processes to efficiently use time and resources.

We are a group of 8 students from Luleå University of Technology in Sweden that has developed this work during a project course on the Master Programme in Computer Science and Engineering, with specialisation Information and Communication Technology. Our work combines some more or less well-known AI tools for Transcribtion, Diarization, Translation and text summarization.

## Models Used

- [Whisper](https://github.com/openai/whisper): Handles transcription.
- [NeMo](https://github.com/NVIDIA/NeMo): Handles diarization.
- [Mistral7b OpenHermes 2.5](https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF) with [LLama-index](https://github.com/run-llama/llama_index): Utilized for summarization, requires GPU
- [Argos-translate](https://github.com/argosopentech/argos-translate): Provides translation functionality.

## Installation

### Prerequisites

- **Docker Engine**: Install Docker Desktop or another Docker version compatible with your system.

### Installation Steps

#### Backend and Frontend Setup


- Run after installing Docker Engine. This script builds both the backend and frontend without using GPU.
    ```
    ./start.sh
    ```
    to run with GPU:
    ```
    ./start.sh gpu
    ```
- Alternatively, navigate to the respective backend and frontend folders and build and deploy separetely
    ```
    ./backend.sh build 
    ./backend.sh run
    ``` 
    with GPU:
    ```
    ./backend.sh gpu build 
    ./backend.sh gpu run
    ``` 


    ```
    ./frontend.sh build
    ./frontend.sh run
    ``` 

- Running with Kubernetes and Helm

    See the [README](https://github.com/Racix/Project-AI-Translation/tree/rebased-kubernetes) in the rebased-kubernetes branch for instructions.


 - Running live-transcription: 

   See the [README](https://github.com/Racix/Project-AI-Translation/tree/main/sound_driver) in the sound_driver folder for instructions.
