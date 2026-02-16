"""Main entry point for the Personalized Agentic Assistant."""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.core import AgenticAssistant
from services.speech import SpeechService
from utils.config import config
from utils.logger import logger

console = Console()


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        Personalized Agentic Assistant v1.0                ║
    ║        Voice-First AI Digital Concierge                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def print_help():
    """Print help information."""
    help_text = """
    [bold]Available Commands:[/bold]
    
    [cyan]Voice Commands:[/cyan]
    - "Book me a cab to [destination]"
    - "Find Italian restaurants nearby"
    - "What's the weather like?"
    - "I'm hungry, get me a ride to a good restaurant"
    
    [cyan]Text Commands:[/cyan]
    - Type your request instead of speaking
    - Type 'quit' or 'exit' to close the application
    - Type 'reset' to clear conversation history
    - Type 'help' to show this message
    - Type 'test' to test microphone
    
    [cyan]Tips:[/cyan]
    - Speak clearly and naturally
    - Wait for the "Listening..." prompt before speaking
    - Location is automatically detected via GPS
    """
    console.print(Panel(help_text, title="Help", border_style="green"))


def run_voice_mode(assistant: AgenticAssistant, speech_service: SpeechService):
    """Run the assistant in voice mode.
    
    Args:
        assistant: AgenticAssistant instance
        speech_service: SpeechService instance
    """
    console.print("\n[bold green]Voice Mode Activated[/bold green]")
    console.print("Speak your commands or type 'text' to switch to text mode\n")
    
    # Greet the user
    greeting = assistant.get_greeting()
    console.print(f"[bold blue]Assistant:[/bold blue] {greeting}\n")
    speech_service.speak(greeting)
    
    while True:
        try:
            # Check if user wants to type instead
            console.print("[yellow]Press Enter to speak, or type your message:[/yellow]")
            user_text_input = input().strip()
            
            if user_text_input:
                # Handle text commands
                if user_text_input.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                elif user_text_input.lower() == 'reset':
                    assistant.reset_conversation()
                    console.print("[green]Conversation reset[/green]")
                    continue
                elif user_text_input.lower() == 'help':
                    print_help()
                    continue
                elif user_text_input.lower() == 'test':
                    speech_service.test_microphone()
                    continue
                elif user_text_input.lower() == 'text':
                    console.print("[cyan]Switching to text-only mode[/cyan]")
                    return 'text'
                
                user_input = user_text_input
            else:
                # Voice input
                console.print("[bold cyan]🎤 Listening...[/bold cyan]")
                user_input = speech_service.listen()
                
                if not user_input:
                    console.print("[yellow]No input detected. Please try again.[/yellow]")
                    continue
                
                console.print(f"[bold green]You:[/bold green] {user_input}\n")
            
            # Process the request
            with console.status("[bold green]Thinking...", spinner="dots"):
                response = assistant.process_request(user_input)
            
            output = response.get("output", "I'm not sure how to help with that.")
            
            # Display response
            console.print(f"[bold blue]Assistant:[/bold blue] {output}\n")
            
            # Speak the response
            speech_service.speak(output)
            
            # Display any deep links
            if response.get("intermediate_steps"):
                for step in response["intermediate_steps"]:
                    if len(step) > 1:
                        tool_result = step[1]
                        if isinstance(tool_result, dict) and "deep_link" in tool_result:
                            console.print(f"[bold cyan]🔗 Deep Link:[/bold cyan] {tool_result['deep_link']}\n")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'quit' to exit or press Enter to continue.[/yellow]")
            continue
        except Exception as e:
            logger.error(f"Error in voice mode: {e}")
            console.print(f"[bold red]Error:[/bold red] {e}\n")


def run_text_mode(assistant: AgenticAssistant):
    """Run the assistant in text-only mode.
    
    Args:
        assistant: AgenticAssistant instance
    """
    console.print("\n[bold green]Text Mode Activated[/bold green]")
    console.print("Type your commands or 'quit' to exit\n")
    
    # Greet the user
    greeting = assistant.get_greeting()
    console.print(f"[bold blue]Assistant:[/bold blue] {greeting}\n")
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("[bold green]You[/bold green]").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif user_input.lower() == 'reset':
                assistant.reset_conversation()
                console.print("[green]Conversation reset[/green]")
                continue
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'voice':
                console.print("[cyan]Voice mode requires speech dependencies[/cyan]")
                continue
            
            # Process the request
            with console.status("[bold green]Thinking...", spinner="dots"):
                response = assistant.process_request(user_input)
            
            output = response.get("output", "I'm not sure how to help with that.")
            
            # Display response
            console.print(f"[bold blue]Assistant:[/bold blue] {output}\n")
            
            # Display any deep links
            if response.get("intermediate_steps"):
                for step in response["intermediate_steps"]:
                    if len(step) > 1:
                        tool_result = step[1]
                        if isinstance(tool_result, dict) and "deep_link" in tool_result:
                            console.print(f"[bold cyan]🔗 Deep Link:[/bold cyan] {tool_result['deep_link']}\n")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'quit' to exit.[/yellow]")
            continue
        except Exception as e:
            logger.error(f"Error in text mode: {e}")
            console.print(f"[bold red]Error:[/bold red] {e}\n")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Personalized Agentic Assistant - Voice-First AI Digital Concierge"
    )
    parser.add_argument(
        "--no-voice",
        action="store_true",
        help="Disable voice mode and use text-only interface"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration file"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Verify API key
    use_openrouter = config.get("agent.use_openrouter", False)
    
    if use_openrouter:
        if not config.openrouter_api_key:
            console.print(
                "[bold red]ERROR:[/bold red] OPENROUTER_API_KEY not found in environment.\n"
                "Please set your API key in config/.env file.",
                style="bold red"
            )
            console.print("\nCreate config/.env file with:\nOPENROUTER_API_KEY=your_key_here")
            console.print("\nGet your key from: https://openrouter.ai/keys")
            sys.exit(1)
        console.print(f"[green]✓ Using OpenRouter API[/green]")
    else:
        if not config.openai_api_key:
            console.print(
                "[bold red]ERROR:[/bold red] OPENAI_API_KEY not found in environment.\n"
                "Please set your API key in config/.env file.",
                style="bold red"
            )
            console.print("\nCreate config/.env file with:\nOPENAI_API_KEY=your_key_here")
            sys.exit(1)
        console.print(f"[green]✓ Using OpenAI API[/green]")
    
    try:
        # Initialize assistant
        console.print("[cyan]Initializing assistant...[/cyan]")
        assistant = AgenticAssistant()
        console.print("[green]✓ Assistant initialized[/green]\n")
        
        # Determine mode
        use_voice = not args.no_voice
        
        if use_voice:
            # Initialize speech service
            try:
                speech_service = SpeechService()
                
                if not speech_service.is_microphone_available():
                    console.print(
                        "[yellow]Warning: Microphone not available. Switching to text mode.[/yellow]\n"
                    )
                    use_voice = False
                else:
                    console.print("[green]✓ Voice service initialized[/green]\n")
            except Exception as e:
                logger.error(f"Failed to initialize speech service: {e}")
                console.print(
                    f"[yellow]Warning: Voice service unavailable ({e}). Switching to text mode.[/yellow]\n"
                )
                use_voice = False
        
        # Show help
        print_help()
        
        # Run appropriate mode
        if use_voice:
            mode = run_voice_mode(assistant, speech_service)
            if mode == 'text':
                run_text_mode(assistant)
        else:
            run_text_mode(assistant)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Application terminated by user.[/yellow]")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        console.print(f"[bold red]Fatal Error:[/bold red] {e}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    main()
