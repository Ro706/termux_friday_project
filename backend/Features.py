from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print

def ShowFeatures():
    console = Console()
    
    # Create a stylish table for features
    table = Table(title="✨ FRIDAY ASSISTANT FEATURES ✨", show_header=True, header_style="bold magenta", border_style="cyan")
    
    table.add_column("Category", style="bold yellow", width=15)
    table.add_column("Command / Feature", style="white")
    table.add_column("Example", style="italic green")

    # App & Web
    table.add_row("🌐 Web & Apps", "Open/Close Applications", "Open Chrome / Close Notepad")
    table.add_row("", "Open Websites", "Open YouTube / Open Facebook")
    table.add_row("", "Google Search", "Search for Python tutorials")
    
    # Media
    table.add_row("🎵 Media", "YouTube Search/Play", "Play Afsanay / Search for AI news on YT")
    table.add_row("", "Spotify Support", "Play song on Spotify")
    table.add_row("", "Volume Control", "Volume up / Mute / Unmute")
    
    # System
    table.add_row("💻 System", "Power Controls", "Shutdown / Restart / Sleep")
    table.add_row("", "Folder Creation", "Create folder name Raj")
    table.add_row("", "Screenshots", "Take a screenshot")
    
    # AI & Info
    table.add_row("🤖 AI & Info", "Chatbot", "General conversation & questions")
    table.add_row("", "Real-time Info", "What is the weather? / Current News")
    table.add_row("", "Image Generation", "Generate image of a futuristic city")
    table.add_row("", "Content Writing", "Write an email to my boss")
    
    # Core
    table.add_row("🛠 Core", "Hardware Info", "Check CPU / Ram information")
    table.add_row("", "Communication", "Send a mail")
    table.add_row("", "Games", "Play Tic Tac Toe / Ball Bouncing / Snake / Rock Paper Scissors")

    # Display everything in a Panel
    console.print(Panel(table, title="[bold white]FRIDAY MENU[/bold white]", border_style="blue", expand=False))
