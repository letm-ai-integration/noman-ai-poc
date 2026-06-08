"""Token and embedding visualization utilities"""

import numpy as np
from typing import List, Dict, Tuple
from transformers import AutoTokenizer, AutoModel
import torch
from src.config import EMBEDDING_MODEL, DEVICE


class TokenVisualizer:
    """Visualize tokens and token IDs"""

    def __init__(self, model_name: str = "distilgpt2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model_name = model_name

    def visualize_tokens(self, text: str) -> Dict:
        """
        Tokenize text and visualize tokens
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with token information
        """
        # Tokenize
        tokens = self.tokenizer.tokenize(text)
        token_ids = self.tokenizer.encode(text, return_tensors="pt")[0]

        result = {
            "text": text,
            "tokens": tokens,
            "token_ids": token_ids.tolist(),
            "num_tokens": len(tokens),
        }

        return result

    def print_tokens(self, text: str):
        """Pretty print token visualization"""
        result = self.visualize_tokens(text)

        print("\n" + "=" * 60)
        print("TOKEN VISUALIZATION")
        print("=" * 60)
        print(f"Text: {result['text']}")
        print(f"Total Tokens: {result['num_tokens']}")
        print("\nToken Breakdown:")
        print(f"{'Token':<20} {'Token ID':<10}")
        print("-" * 30)

        for token, token_id in zip(result["tokens"], result["token_ids"]):
            # Handle special tokens
            display_token = repr(token) if token.startswith("Ġ") else token
            print(f"{display_token:<20} {token_id:<10}")

        print("=" * 60 + "\n")

        return result

    def analyze_token_efficiency(self, texts: List[str]) -> Dict:
        """
        Analyze token efficiency across multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            Analysis dictionary
        """
        results = {}
        for text in texts:
            token_count = len(self.tokenizer.tokenize(text))
            results[text] = {
                "text_length": len(text),
                "token_count": token_count,
                "tokens_per_char": token_count / len(text) if len(text) > 0 else 0,
            }

        return results


class EmbeddingVisualizer:
    """Visualize embeddings and semantic similarity"""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(DEVICE)
        self.model.eval()

    def get_embeddings(self, text: str) -> np.ndarray:
        """
        Get embeddings for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        with torch.no_grad():
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            ).to(DEVICE)
            outputs = self.model(**inputs)
            # Use mean pooling
            embeddings = outputs.last_hidden_state.mean(dim=1)

        return embeddings[0].cpu().numpy()

    def get_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = self.get_embeddings(text)
            embeddings.append(embedding)
        return np.array(embeddings)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        emb1 = self.get_embeddings(text1)
        emb2 = self.get_embeddings(text2)

        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (
            np.linalg.norm(emb1) * np.linalg.norm(emb2)
        )
        return float(similarity)

    def print_embedding_info(self, text: str):
        """Print embedding information"""
        embedding = self.get_embeddings(text)

        print("\n" + "=" * 60)
        print("EMBEDDING VISUALIZATION")
        print("=" * 60)
        print(f"Text: {text}")
        print(f"Embedding Dimension: {embedding.shape[0]}")
        print(f"\nEmbedding Statistics:")
        print(f"  Mean: {embedding.mean():.6f}")
        print(f"  Std Dev: {embedding.std():.6f}")
        print(f"  Min: {embedding.min():.6f}")
        print(f"  Max: {embedding.max():.6f}")
        print(f"\nFirst 10 embedding values:")
        print(f"  {embedding[:10]}")
        print("=" * 60 + "\n")

        return embedding

    def print_similarity_matrix(self, texts: List[str]):
        """Print similarity matrix for multiple texts"""
        embeddings = self.get_batch_embeddings(texts)

        # Calculate similarity matrix
        similarity_matrix = np.zeros((len(texts), len(texts)))
        for i in range(len(texts)):
            for j in range(len(texts)):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    similarity_matrix[i][j] = np.dot(
                        embeddings[i], embeddings[j]
                    ) / (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]))

        print("\n" + "=" * 60)
        print("SIMILARITY MATRIX")
        print("=" * 60)
        print(f"{'Text':<30} " + "".join([f"T{i:<8}" for i in range(len(texts))]))
        print("-" * (30 + 10 * len(texts)))

        for i, text in enumerate(texts):
            truncated = (text[:27] + "...") if len(text) > 30 else text
            row = f"{truncated:<30} "
            for j in range(len(texts)):
                row += f"{similarity_matrix[i][j]:<8.4f}"
            print(row)

        print("=" * 60 + "\n")

        return similarity_matrix
