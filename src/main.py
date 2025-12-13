
# main.py - demo CLI for speakmath package
from .lexer import lex
from .parser import Parser
from .interpreter import Interpreter

def run_command(text, interp=None):
    if interp is None:
        interp = Interpreter()
    toks = lex(text)
    parser = Parser(toks)
    ast = parser.parse()
    return interp.eval(ast), interp

def demo():
    interp = Interpreter()
    examples = [
        "set x to 5",
        "set nums to [1,2,3,4]",
        "print nums",
        "sum nums",
        "mean nums",
        "product nums",
        "map add 2 over nums",
        "reduce multiply over nums",
        "if 5 > 3 then print 99",
    ]
    print('--- Demo run ---')
    for ex in examples:
        print('> ', ex)
        try:
            out, interp = run_command(ex, interp)
            if out is not None:
                print('=>', out)
        except Exception as e:
            print('ERROR:', e)
    print('--- End demo ---')

def repl():
    print("SpeakMath Interactive REPL")
    print("Type 'help' for commands, or 'exit'/'quit' to leave.")
    interp = Interpreter()
    
    # Optional: nicer input if readline available
    try:
        import readline
    except ImportError:
        pass

    while True:
        try:
            text = input(">> ")
            if text.lower() in ("exit", "quit"):
                break
            if text.lower() == "help":
                print("\n========================= SPEAKMATH HELP =========================")
                print("BASIC:")
                print("  set <var> to <val>       : Assign variable (e.g., 'set x to 5')")
                print("  print <expr>             : Print value (e.g., 'print x', 'print [1,2]')")
                print("\nMATH & STATS:")
                print("  sum <list>               : Sum total (e.g., 'sum [1, 2, 3]')")
                print("  mean <list>              : Average (e.g., 'mean [10, 20]')")
                print("  product <list>           : Multiply all (e.g., 'product [2, 3]')")
                print("  max / min <list>         : Find largest/smallest")
                print("  sort <list>              : Sort numbers")
                print("\nFUNCTIONAL:")
                print("  map <op> <n> over <list> : Apply op to all (e.g., 'map add 2 over [1,2]')")
                print("  reduce <op> over <list>  : Combine all (e.g., 'reduce multiply over [1,2]')")
                print("\nNATURAL LANGUAGE (AI):")
                print("  You can ask in English! The AI will interpret your intent.")
                print("  Examples:")
                print("    'find the average of these numbers [10, 20]'")
                print("    'tally up the cost [5, 10, 2]'")
                print("    'arrange from high to low [1, 5, 2]'")
                print("\nCONTROLS:")
                print("  help                     : Show this menu")
                print("  exit / quit              : Exit REPL")
                print("==================================================================\n")
                continue
                
            if not text.strip():
                continue
            out, interp = run_command(text, interp)
            if out is not None:
                print("=>", out)
        except KeyboardInterrupt:
            print("\nType 'exit' to quit.")
            continue
        except Exception as e:
            # Check if it's a "Unknown command" error (usually ParseError)
            err_msg = str(e)
            if "Unknown command" in err_msg or "Unexpected token" in err_msg:
                print(f"ERROR: {err_msg}")
                print("Tip: I didn't understand that. Please REPHRASE your command or type 'help' to see valid examples.")
                print("Example: 'find the sum of [1, 2, 3]'")
            else:
                print("ERROR:", err_msg)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        repl()
