#!/usr/bin/env python3
"""Setup script to download LLM and embedding models"""

import sys
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel
from transformers import logging

logging.set_verbosity_error()


def download_models():
    """Download and cache required models"""
    try:
        print("🤖 Downloading LLM and embedding models...")
        print("   Models will be cached for future use (~1GB download)")
        
        print("   Downloading distilgpt2 model...", end="", flush=True)
        AutoTokenizer.from_pretrained("distilgpt2")
        AutoModelForCausalLM.from_pretrained("distilgpt2")
        print(" ✓")

        print("   Downloading embedding model...", end="", flush=True)
        AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        print(" ✓")
        
        print("✓ Models downloaded and cached")
        return True
        
    except Exception as e:
        print(f"\n✗ Error downloading models: {str(e)}")
        return False


if __name__ == "__main__":
    success = download_models()
    sys.exit(0 if success else 1)
