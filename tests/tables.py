from rich.console import Console
from rich.table import Table

console = Console()

table = Table(title="Table demo: grid table with 'pretty' style")
table.add_column("This is", style="cyan")
table.add_column("a header", style="magenta")
table.add_column("row", style="green", justify="center")  # Set justify here

table.add_row("See", "I", "This is a left aligned row")
table.add_row("See", "I", "This is a middle aligned row")
table.add_row("This", "is", "an ordinary row")

console.print(table)