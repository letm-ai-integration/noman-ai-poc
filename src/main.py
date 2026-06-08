"""Main CLI for LLM QnA Bot"""

import sys
import argparse
from typing import Optional
from src.llm_client import LLMClient
from src.prompt_manager import PromptManager
from src.token_visualizer import TokenVisualizer, EmbeddingVisualizer
from src.config import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser"""
    parser = argparse.ArgumentParser(
        description="LLM QnA Bot with Token Visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python -m src.main --mode interactive

  # Single question with QA role
  python -m src.main --question "What is Python?" --role qa

  # Custom temperature
  python -m src.main --question "Write a poem" --temperature 1.5 --max-tokens 80

  # Compare temperatures
  python -m src.main --question "Tell a story" --compare-temps

  # Analyze tokens
  python -m src.main --analyze-tokens "Hello world"

  # Visualize embeddings
  python -m src.main --visualize-embeddings "What is AI?"
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["interactive", "single"],
        default="interactive",
        help="Operation mode (default: interactive)",
    )

    parser.add_argument(
        "--question",
        type=str,
        help="Question to ask the bot",
    )

    parser.add_argument(
        "--role",
        choices=["qa", "tutor", "creative", "assistant"],
        default="qa",
        help="Prompt role (default: qa)",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Sampling temperature (default: {DEFAULT_TEMPERATURE})",
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"Maximum tokens to generate (default: {DEFAULT_MAX_TOKENS})",
    )

    parser.add_argument(
        "--top-p",
        type=float,
        default=0.9,
        help="Nucleus sampling parameter (default: 0.9)",
    )

    parser.add_argument(
        "--compare-temps",
        action="store_true",
        help="Compare responses with different temperatures",
    )

    parser.add_argument(
        "--compare-tokens",
        action="store_true",
        help="Compare responses with different max token values",
    )

    parser.add_argument(
        "--analyze-tokens",
        type=str,
        help="Analyze tokens for a given text",
    )

    parser.add_argument(
        "--visualize-embeddings",
        nargs="+",
        help="Visualize embeddings for given texts",
    )

    parser.add_argument(
        "--similarity",
        nargs=2,
        metavar=("TEXT1", "TEXT2"),
        help="Calculate similarity between two texts",
    )

    return parser


def print_welcome():
    """Print welcome message"""
    print("\n" + "=" * 80)
    print("Welcome to LLM QnA Bot with Token Visualization")
    print("=" * 80)
    print("\nAvailable Commands:")
    print("  ask <question>          - Ask a question")
    print("  role <role_name>        - Change role (qa, tutor, creative, assistant)")
    print("  temp <value>            - Set temperature (0.1-2.0)")
    print("  tokens <value>          - Set max tokens")
    print("  visualize <text>        - Visualize tokens for text")
    print("  embedding <text>        - Get embedding info")
    print("  similarity <text1|text2> - Compare text similarity")
    print("  history                 - Show conversation history")
    print("  clear                   - Clear conversation history")
    print("  roles                   - Show available roles")
    print("  help                    - Show this help message")
    print("  exit/quit               - Exit the bot")
    print("=" * 80 + "\n")


def interactive_mode():
    """Run in interactive mode"""
    print_welcome()

    llm = LLMClient()
    prompt_manager = PromptManager()
    token_viz = TokenVisualizer()
    embed_viz = EmbeddingVisualizer()

    temperature = DEFAULT_TEMPERATURE
    max_tokens = DEFAULT_MAX_TOKENS
    current_role = "qa"

    print(f"Current Settings: Role={current_role}, Temp={temperature}, MaxTokens={max_tokens}\n")

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            # Parse command
            parts = user_input.split(" ", 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command in ["exit", "quit"]:
                print("\nThank you for using LLM QnA Bot. Goodbye!")
                break

            elif command == "ask":
                if not args:
                    print("Usage: ask <question>")
                    continue
                
                print(f"\nProcessing with role '{current_role}'...")
                prompt = prompt_manager.create_prompt(args, role=current_role)
                result = llm.generate(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    visualize_tokens=False,
                )
                llm.print_response(result)
                prompt_manager.add_to_history(args, result["response"])

            elif command == "role":
                if not args:
                    print("Available roles:", ", ".join(prompt_manager.get_available_roles().keys()))
                    continue
                
                if args in prompt_manager.get_available_roles():
                    current_role = args
                    print(f"Role changed to: {current_role}")
                else:
                    print(f"Unknown role: {args}")

            elif command == "temp":
                try:
                    temp_val = float(args)
                    if 0.1 <= temp_val <= 2.0:
                        temperature = temp_val
                        print(f"Temperature set to: {temperature}")
                    else:
                        print("Temperature must be between 0.1 and 2.0")
                except ValueError:
                    print("Invalid temperature value")

            elif command == "tokens":
                try:
                    tok_val = int(args)
                    if 1 <= tok_val <= 512:
                        max_tokens = tok_val
                        print(f"Max tokens set to: {max_tokens}")
                    else:
                        print("Max tokens must be between 1 and 512")
                except ValueError:
                    print("Invalid tokens value")

            elif command == "visualize":
                if not args:
                    print("Usage: visualize <text>")
                    continue
                token_viz.print_tokens(args)

            elif command == "embedding":
                if not args:
                    print("Usage: embedding <text>")
                    continue
                embed_viz.print_embedding_info(args)

            elif command == "similarity":
                if "|" not in args:
                    print("Usage: similarity <text1|text2>")
                    continue
                texts = args.split("|")
                if len(texts) == 2:
                    sim = embed_viz.calculate_similarity(texts[0].strip(), texts[1].strip())
                    print(f"\nSimilarity: {sim:.4f}")
                else:
                    print("Please provide exactly 2 texts separated by |")

            elif command == "history":
                if prompt_manager.conversation_history:
                    print("\nConversation History:")
                    for i, (q, a) in enumerate(prompt_manager.conversation_history, 1):
                        print(f"\n{i}. Q: {q}")
                        print(f"   A: {a[:100]}..." if len(a) > 100 else f"   A: {a}")
                else:
                    print("No conversation history yet")

            elif command == "clear":
                prompt_manager.clear_history()
                print("Conversation history cleared")

            elif command == "roles":
                print("\nAvailable Roles:")
                for role, desc in prompt_manager.get_available_roles().items():
                    print(f"  {role}: {desc}")

            elif command == "help":
                print_welcome()

            else:
                # Treat as question if not a command
                if command != "help":
                    prompt = prompt_manager.create_prompt(user_input, role=current_role)
                    result = llm.generate(
                        prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        visualize_tokens=False,
                    )
                    llm.print_response(result)
                    prompt_manager.add_to_history(user_input, result["response"])

        except KeyboardInterrupt:
            print("\n\nExiting... Goodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def single_question_mode(args):
    """Process single question and exit"""
    llm = LLMClient()
    prompt_manager = PromptManager()

    prompt = prompt_manager.create_prompt(
        args.question,
        role=args.role,
    )

    print(f"Using role: {args.role}")

    result = llm.generate(
        prompt,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        visualize_tokens=True,
    )

    llm.print_response(result)

    if args.compare_temps:
        llm.compare_temperatures(prompt, max_tokens=args.max_tokens)

    if args.compare_tokens:
        llm.compare_max_tokens(prompt, temperature=args.temperature)


def analyze_tokens_mode(text: str):
    """Analyze tokens for given text"""
    token_viz = TokenVisualizer()
    token_viz.print_tokens(text)


def visualize_embeddings_mode(texts: list):
    """Visualize embeddings for given texts"""
    embed_viz = EmbeddingVisualizer()

    for text in texts:
        embed_viz.print_embedding_info(text)

    if len(texts) > 1:
        embed_viz.print_similarity_matrix(texts)


def similarity_mode(text1: str, text2: str):
    """Calculate similarity between two texts"""
    embed_viz = EmbeddingVisualizer()
    sim = embed_viz.calculate_similarity(text1, text2)

    print("\n" + "=" * 60)
    print("SIMILARITY ANALYSIS")
    print("=" * 60)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Similarity: {sim:.4f}")
    print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        if args.analyze_tokens:
            analyze_tokens_mode(args.analyze_tokens)

        elif args.visualize_embeddings:
            visualize_embeddings_mode(args.visualize_embeddings)

        elif args.similarity:
            similarity_mode(args.similarity[0], args.similarity[1])

        elif args.mode == "interactive":
            if args.question:
                # Single question in interactive context
                llm = LLMClient()
                prompt_manager = PromptManager()
                prompt = prompt_manager.create_prompt(args.question, role=args.role)
                result = llm.generate(
                    prompt,
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                )
                llm.print_response(result)
            else:
                interactive_mode()

        elif args.mode == "single":
            if not args.question:
                print("Error: --question required in single mode")
                sys.exit(1)
            single_question_mode(args)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
