```
make clean
make
make samples
```

This system processes input files from the samples directory, tokenises their content,
and reads back the tokenised output for display. Tokens are marked with approximate
source code locations. While the grammar isn't yet applied, the system attempts to
identify reserved words (later ensuring they are not used inappropriately elsewhere).

