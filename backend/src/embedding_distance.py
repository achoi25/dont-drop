from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine, euclidean
import numpy as np

CONTROL = "i like spaghetti and meatballs"

model = SentenceTransformer("all-MiniLM-L6-v2")
control_embedding = model.encode(CONTROL)

while True:
    user_input = input("\nEnter a sentence (or 'quit' to exit): ").strip()
    if user_input.lower() in ("quit", "q", "exit"):
        break
    if not user_input:
        continue

    input_embedding = model.encode(user_input)

    cos_dist = cosine(control_embedding, input_embedding)
    cos_sim = 1 - cos_dist
    euc_dist = euclidean(control_embedding, input_embedding)

    print(f"\nControl:            \"{CONTROL}\"")
    print(f"Input:              \"{user_input}\"")
    print(f"Cosine similarity:  {cos_sim:.4f}")
    print(f"Cosine distance:    {cos_dist:.4f}")
    print(f"Euclidean distance: {euc_dist:.4f}")
