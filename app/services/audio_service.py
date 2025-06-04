# import os
# import requests
# import google.generativeai as genai

# # Constants (replace with your actual values or manage via .env)
# FACEBOOK_GRAPH_API_BASE = "https://graph.facebook.com/v22.0"
# TOKEN = "EAAQKF56ZAbJQBO3eHvyzD8AERlnLM7hAvtAIZCcSYubLA7JqPq7iv2NGlzlgDfX1DnJ9CJl9ZANyHdiHYNztdvAjf2C4XKWXFMBCjqTagNJDV4VYV59VhzLQ76kZBjrVP3XDsa2UeqBmT9lr01zgImVXPcmeDsyf6KXOaDk61yFzMKS5BkFZBhDX4tsMfuJ4ZA5QZDZD"
# GOOGLE_API_KEY = "AIzaSyApUfQvy62AULXZ98fhe5tdYxzYRNsDM6I"

# # Configure Google API key
# genai.configure(api_key=GOOGLE_API_KEY)

# def transcribe_audio_from_facebook(audio_id):
#     """Fetches audio by ID from Facebook, sends it to Google for transcription, and returns the transcript."""
#     audio_metadata_url = f"{FACEBOOK_GRAPH_API_BASE}/{audio_id}"

#     headers = {
#         "Authorization": f"Bearer {TOKEN}"
#     }

#     try:
#         # Step 1: Fetch metadata (to get download URL)
#         meta_resp = requests.get(audio_metadata_url, headers=headers)
#         meta_resp.raise_for_status()
#         audio_url = meta_resp.json().get("url")

#         if not audio_url:
#             raise ValueError("Audio source URL not found in metadata response")

#         # Step 2: Download the audio
#         local_audio_file = f"{audio_id}.wav"
#         audio_resp = requests.get(audio_url, headers=headers)
#         audio_resp.raise_for_status()
#         with open(local_audio_file, "wb") as f:
#             f.write(audio_resp.content)
#         print(f"Downloaded audio: {local_audio_file}")

#         # Step 3: Upload audio to Gemini
#         uploaded_file = genai.upload_file(path=local_audio_file, mime_type="audio/wav")

#         # Step 4: Transcribe using Gemini
#         model = genai.GenerativeModel(model_name="gemini-2.5-flash-preview-05-20")# or "gemini-2.5-flash-preview-05-20"
#         prompt = "Transcribe the speech in the audio file."
#         response = model.generate_content([prompt, uploaded_file])

#         # Clean up: remove local file and uploaded Gemini file
#         os.remove(local_audio_file)
#         genai.delete_file(uploaded_file.name)

#         return response.text

#     except requests.RequestException as e:
#         return f"Network error: {e}"
#     except Exception as e:
#         return f"Error: {e}"

# # Entry point for script execution
# if __name__ == "__main__":
#     # Replace with a valid audio ID for testing
#     test_audio_id = "576851091746874"
#     result = transcribe_audio_from_facebook(test_audio_id)
#     print("Transcription Result:\n", result)
