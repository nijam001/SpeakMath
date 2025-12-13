# Syntax Definition (BNF / EBNF)

**COMMAND LEVEL**

```ebnf
<Command> ::= <ComputeCommand>
            | <AssignCommand>
            | <ConditionalCommand>
            | <FunctionalCommand>
            | <PrintCommand>
            | <SequenceCommand>
```

**COMPUTATION COMMANDS**

```ebnf
<ComputeCommand> ::= <Verb> <Target>

<Verb> ::= "sum" | "add" | "total"
         | "mean" | "average"
         | "multiply" | "product"
         | "max" | "min"
         | "sort ascending" | "sort descending"

<Target> ::= <List> | <Variable> | <Expression>

<List> ::= <Number> { "," <Number> }
```

**ASSIGNMENT COMMAND**

```ebnf
<AssignCommand> ::= "set" <Variable> "to" <Expression>
```

**CONDITIONAL COMMAND**

```ebnf
<ConditionalCommand> ::= "if" <BooleanExpr> "then" <Command>

<BooleanExpr> ::= <Expression> <Comparator> <Expression>

<Comparator> ::= ">" | "<" | "==" | "!=" | ">=" | "<="
```

**FUNCTIONAL COMMANDS**

```ebnf
<FunctionalCommand> ::= "map" <Verb> <Number>? "over" <Target>
                      | "reduce" <Verb> "over" <Target>
```

**FUNCTIONAL COMPOSITION**

```ebnf
<SequenceCommand> ::= <FunctionalCommand> "then" <FunctionalCommand>
```

**PRINT COMMAND**

```ebnf
<PrintCommand> ::= "print" <Expression>
```

**EXPRESSIONS**

```ebnf
<Expression> ::= <Term> { ("+" | "-") <Term> }

<Term> ::= <Factor> { ("*" | "/") <Factor> }

<Factor> ::= <Number> | <Variable> | "(" <Expression> ")" | <List>
```

**TOKENS**

```ebnf
<Number> ::= <Digit> | <Digit> <Number>
<Digit> ::= "0" | "1" | ... | "9"
<Variable> ::= <Letter> { <Letter> | <Digit> }
<Letter> ::= "a" | "b" | ... | "z" | "A" | "B" | ... | "Z"
```
