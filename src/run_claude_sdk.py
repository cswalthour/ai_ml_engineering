# libraries supporting env setup
import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic

# load environment variables
load_dotenv()

# load custom modules
from utils.utils_claude import claude_execute

EXIT_COMMANDS = frozenset({"exit", "quit", "q"})

# main function
def main() -> None:
    # create claude client
    claude_client = Anthropic(api_key=os.getenv("claude_api_key"))

    # initialize conversation
    conversation: list = []

    print("Interactive Claude (Anthropic API). Type a message; use exit, quit, or q to stop.\n")

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            sys.exit(0)

        if not user_message:
            continue

        if user_message.lower() in EXIT_COMMANDS:
            print("Bye.")
            break

        print("Claude:")
        conversation = claude_execute(claude_client, conversation, user_message)
        print()


if __name__ == "__main__":
    main()
