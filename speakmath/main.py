
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
    print("Type 'exit' or 'quit' to leave.")
    interp = Interpreter()
    while True:
        try:
            text = input(">> ")
            if text.lower() in ("exit", "quit"):
                break
            if not text.strip():
                continue
            out, interp = run_command(text, interp)
            if out is not None:
                print("=>", out)
        except Exception as e:
            print("ERROR:", e)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        repl()
