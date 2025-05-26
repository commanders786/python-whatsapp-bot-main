# import requests
# import hashlib
# import os
# import whisper
# from indic_transliteration import sanscript
# from indic_transliteration.sanscript import transliterate

# # Configuration
# API_URL = "https://graph.facebook.com/v22.0/575516075170449"
# TOKEN = "EAAQKF56ZAbJQBO3eHvyzD8AERlnLM7hAvtAIZCcSYubLA7JqPq7iv2NGlzlgDfX1DnJ9CJl9ZANyHdiHYNztdvAjf2C4XKWXFMBCjqTagNJDV4VYV59VhzLQ76kZBjrVP3XDsa2UeqBmT9lr01zgImVXPcmeDsyf6KXOaDk61yFzMKS5BkFZBhDX4tsMfuJ4ZA5QZDZD  "  # Replace with your actual token
# AUDIO_FILE = "audio.wav"

# # Headers for API requests
# headers = {"Authorization": f"Bearer {TOKEN}"}

# def fetch_audio_metadata():
#     """Fetch metadata for the audio file from the Graph API."""
#     try:
#         response = requests.get(API_URL, headers=headers)
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException as e:
#         print(f"Failed to fetch metadata: {e}")
#         return None

# def download_audio(url):
#     """Download the audio file from the provided URL."""
#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         with open(AUDIO_FILE, "wb") as f:
#             f.write(response.content)
#         print(f"Audio downloaded successfully as {AUDIO_FILE}")
#         return True
#     except requests.RequestException as e:
#         print(f"Failed to download audio: {e}")
#         return False

# def verify_file(file_path, expected_size, expected_sha256):
#     """Verify the downloaded file's size and SHA-256 hash."""
#     if not os.path.exists(file_path):
#         print(f"File {file_path} does not exist")
#         return False

#     actual_size = os.path.getsize(file_path)
#     if actual_size != expected_size:
#         print(f"File size mismatch: expected {expected_size} bytes, got {actual_size} bytes")
#         return False

#     sha256_hash = hashlib.sha256()
#     with open(file_path, "rb") as f:
#         for byte_block in iter(lambda: f.read(4096), b""):
#             sha256_hash.update(byte_block)
#     actual_hash = sha256_hash.hexdigest()
#     if actual_hash != expected_sha256:
#         print(f"SHA-256 hash mismatch: expected {expected_sha256}, got {actual_hash}")
#         return False

#     print("File verification successful")
#     return True

# def is_malayalam(text):
#     """Check if the text contains Malayalam Unicode characters."""
#     return any('\u0D00' <= c <= '\u0D7F' for c in text)

# def transcribe_audio(file_path):
#     """Transcribe the audio file using Whisper and convert to Manglish if needed."""
#     try:
#         print(f"Transcribing {file_path} ...")
#         model = whisper.load_model("small")  # Use "medium" for better quality
#         result = model.transcribe(file_path)  # Let Whisper auto-detect the language

#         text = result["text"].strip()
#         print("Original Transcription:", text)

#         if is_malayalam(text):
#             try:
#                 manglish_text = transliterate(text, sanscript.MALAYALAM, sanscript.ITRANS)
#                 print("Detected Malayalam. Transliterated to Manglish:")
#                 return manglish_text
#             except Exception as e:
#                 print(f"Transliteration failed: {e}")
#                 return text
#         else:
#             print("Detected English or phonetic Malayalam. Returning original text.")
#             return text
#     except Exception as e:
#         print(f"Transcription failed: {e}")
#         return None

# def main():
#     # Step 1: Fetch metadata
#     metadata = fetch_audio_metadata()
#     if not metadata:
#         return

#     # Extract relevant fields
#     url = metadata.get("url")
#     file_size = metadata.get("file_size")
#     sha256 = metadata.get("sha256")

#     if not url or not file_size or not sha256:
#         print("Incomplete metadata received")
#         return

#     # Step 2: Download the audio (.wav)
#     if not download_audio(url):
#         return

#     # Step 3: Verify the downloaded file
#     if not verify_file(AUDIO_FILE, file_size, sha256):
#         return

#     # Step 4: Transcribe the audio and convert to Manglish
#     text = transcribe_audio(AUDIO_FILE)
#     if text:
#         print("Final Transcription Output:")
#         print(text)
#     else:
#         print("No transcription result returned.")

#     # Step 5: Cleanup
#     # try:
#     #     if os.path.exists(AUDIO_FILE):
#     #         os.remove(AUDIO_FILE)
#     #         print(f"Temporary file {AUDIO_FILE} deleted")
#     # except OSError as e:
#     #     print(f"Failed to delete temporary file: {e}")

# if __name__ == "__main__":
#     main()
