
from sch import parse, tokenize, default_frame, eval, List, Symbol, Int

def test_parser():
    assert parse(tokenize("(+ 1 2)")) == List([Symbol('+'), Int(1), Int(2)])
    assert parse(tokenize("(define x 42)")) == List([Symbol('define'), Symbol('x'), Int(42)])
    print("Parser tests passed!")

def test_eval():
    frame = default_frame()
    assert eval(parse(tokenize("(+ 1 2)")), frame) == Int(3)
    assert eval(parse(tokenize("(* 3 4)")), frame) == Int(12)
    print("Evaluation tests passed!")

def test_functions():
    frame = default_frame()
    eval(parse(tokenize("(define square (lambda (x) (* x x)))")), frame)
    assert eval(parse(tokenize("(square 5)")), frame) == Int(25)
    print("Function tests passed!")

if __name__ == '__main__':
    test_parser()
    test_eval()
    test_functions()
