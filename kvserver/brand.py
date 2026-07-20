from pyfiglet import Figlet
from rich.console import Console
from PIL import Image

def print_logo(logo_path):
    console = Console()
    f = Figlet(font="big")
    text = f.renderText("KivyDevClient")
    left_margin = 21  # Number of spaces
    # Add left margin to each line
    text = "\n".join(" " * int(left_margin+10) + line for line in text.splitlines())

    #chars = "o%#*+=-:. "
    chars = " .:-=+*#%o"
    img = Image.open(logo_path).convert("L")
    img = img.resize((80, 40))


    for y in range(img.height):
        line = ""
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            line += chars[pixel * len(chars) // 256]
        #print(line)
        console.print(f"{' '*left_margin}[bold cyan]{line}[/bold cyan]")

    console.print(f"[bold cyan]{text}[/bold cyan]")
    
