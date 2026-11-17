# Architecture

The model check passes instructions and text to `components/call_model.py`, the only module that contacts OpenAI. The wrapper reads the model name from `config/settings.yaml` and returns the answer and token count.

Add the evidence-check workflow here as it takes shape.
