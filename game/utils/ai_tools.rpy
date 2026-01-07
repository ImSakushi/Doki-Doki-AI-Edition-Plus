init python:
    import os
    import random
    import requests
    try:
        import ollama
        import httpx
        OLLAMA_AVAILABLE = True
    except Exception:
        ollama = None
        httpx = None
        OLLAMA_AVAILABLE = False


    class TextModel:


        def getLLM(self, prompt):
            if persistent.chatProvider == "openai":
                return self._openai_chat(prompt)
            return self._ollama_chat(prompt)


        def _ollama_chat(self, prompt):
            if not OLLAMA_AVAILABLE:
                return False, "<|Error|> Ollama python module not installed. Install it or switch to OpenAI in settings."
            seed = random.random() if persistent.seed == "random" else persistent.seed

            options = ollama.Options(temperature=float(f".{persistent.temp}"), stop=["[INST", "[/INST", "[END]"],
            num_ctx=int(persistent.context_window), seed=seed, num_predict=200)

            try:
                response = ollama.chat(model=persistent.chatModel, messages=prompt, options=options)
                result = response['message']['content']

                renpy.log(f"RAW RESPONSE: {result}")

                if "[END]" not in result:
                    return result.strip() + " [END]"
                return result.strip()

            except httpx.ConnectError:
                return False, "<|Error|> You don't have ollama running."
            except ollama.ResponseError as e:
                if e.status_code == 404:
                    return False, f"<|Error|> You dont have the model \"{persistent.chatModel}\" installed! Go to settings and install this model (if it exists)."
                return False, f"<|Error|> {e.error}"


        def _openai_chat(self, prompt):
            if not persistent.chatToken:
                return False, "<|Error|> Missing OpenAI API key. Go to Settings and set your API key."
            if not persistent.chatModel or persistent.chatModel == "None":
                return False, "<|Error|> Missing ChatGPT model name. Go to Settings and set your model."

            seed = None
            if persistent.seed != "random":
                try:
                    seed = int(persistent.seed)
                except ValueError:
                    seed = None

            payload = {
                "model": persistent.chatModel,
                "messages": prompt,
                "temperature": float(f"0.{persistent.temp}"),
                "max_tokens": 200,
                "stop": ["[INST", "[/INST", "[END]"],
            }

            if seed is not None:
                payload["seed"] = seed

            response = None
            try:
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {persistent.chatToken}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()
                result = data["choices"][0]["message"]["content"]

                renpy.log(f"RAW RESPONSE: {result}")

                if "[END]" not in result:
                    return result.strip() + " [END]"
                return result.strip()

            except requests.exceptions.RequestException as e:
                try:
                    error_info = response.json().get("error", {}) if response is not None else {}
                    error_message = error_info.get("message", str(e))
                except Exception:
                    error_message = str(e)
                return False, f"<|Error|> {error_message}"






