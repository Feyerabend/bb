


```
make clean
make
make samples
```

This system tokenises input files from the samples directory and reads the tokenised output to display it.
Tokens are annotated with approximate locations in the source code. Although the grammar isn't applied yet,
the system makes a best-effort guess to identify reserved words, which are prohibited from being used as
anything else.
