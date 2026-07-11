from google import genai

client = genai.Client(vertexai=True, project="dontdrop-502116", location="us-central1")
response = client.models.generate_content(
    model="gemini-2.5-flash-lite", contents="Say hello!"
)
print(response.text)
