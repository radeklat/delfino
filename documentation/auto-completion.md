# Auto-completion development notes

The auto-completion is based on several sources:
- [Click auto-completion](https://click.palletsprojects.com/en/8.0.x/shell-completion/?highlight=completions#enabling-completion)
- Invoke implementation of dynamic completion
- [`typer` installation of completions](https://github.com/tiangolo/typer/blob/master/typer/completion.py) and shell detection with [`shellingham`](https://github.com/sarugaku/shellingham)

## Invoke implementation

The following script is used by Invoke in `.bashrc`:

```bash
# Invoke tab-completion script to be sourced with Bash shell.
# Known to work on Bash 3.x, untested on 4.x.

_complete_invoke() {
    local candidates

    # COMP_WORDS contains the entire command string up til now (including
    # program name).
    # We hand it to Invoke so it can figure out the current context: spit back
    # core options, task names, the current task's options, or some combo.
    candidates=`invoke --complete -- ${COMP_WORDS[*]}`

    # `compgen -W` takes list of valid options & a partial word & spits back
    # possible matches. Necessary for any partial word completions (vs
    # completions performed when no partial words are present).
    #
    # $2 is the current word or token being tabbed on, either empty string or a
    # partial word, and thus wants to be compgen'd to arrive at some subset of
    # our candidate list which actually matches.
    #
    # COMPREPLY is the list of valid completions handed back to `complete`.
    COMPREPLY=( $(compgen -W "${candidates}" -- $2) )
}


# Tell shell builtin to use the above for completing our invocations.
# * -F: use given function name to generate completions.
# * -o default: when function generates no results, use filenames.
# * positional args: program names to complete for.
complete -F _complete_invoke -o default invoke inv
```
