# DoRiS - Diarization of Recordings in Speech-to-text

This branch was specifically created to deploy the project onto Googles Kubernetes Engine. 

All the images the pods are using are already pushed to a public docker repository so there is no need to build new images.
If you have a GKE cluster running with a GPU attached to a node then all you need to do is git clone this branch and run the following command.

To start the cluster write

```helm install name ./project-chart ```

To delete the cluster write

```helm uninstall name```

If you do not have a GKE cluster with a GPU attached node. Then visit the main branch to learn how to run it locally with docker.
