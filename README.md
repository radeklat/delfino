<h1 align="center" style="border-bottom: none;">🧰&nbsp;&nbsp;Delfino&nbsp;&nbsp;🧰</h1>
<h3 align="center">A collection of command line helper scripts wrapping tools used during Python development.</h3>

<p align="center">
    <a href="https://app.circleci.com/pipelines/github/radeklat/delfino?branch=main">
        <img alt="CircleCI" src="https://img.shields.io/circleci/build/github/radeklat/delfino">
    </a>
    <a href="https://app.codecov.io/gh/radeklat/delfino/">
        <img alt="Codecov" src="https://img.shields.io/codecov/c/github/radeklat/delfino">
    </a>
    <a href="https://github.com/radeklat/delfino/tags">
        <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/tag/radeklat/delfino">
    </a>
    <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2021">
    <a href="https://github.com/radeklat/delfino/commits/main">
        <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/radeklat/delfino">
    </a>
</p>

<!--
    How to generate TOC from PyCharm:
    https://github.com/vsch/idea-multimarkdown/wiki/Table-of-Contents-Extension
-->
[TOC levels=1,2 markdown formatted bullet hierarchy]: # "Table of content"

# Table of content
- [Installation](#installation)
- [Usage](#usage)

# Installation

TODO

# Usage

TODO

<!--

## Minimal plugin

```python
import click

from delfino.contexts import pass_app_context, AppContext


@click.command()
@pass_app_context
def plugin_test(app_context: AppContext):
    """Tests commands placed in the `commands` folder are loaded."""
    print(app_context.py_project_toml.tool.delfino.plugins)
```

 -->

<!--

# Install completions

Based on [Click documentation](https://click.palletsprojects.com/en/8.0.x/shell-completion/?highlight=completions#enabling-completion) and Invoke implementation of dynamic completion:

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

Put into `~/.bashrc`:

```bash
_complete_delfino() {
    eval "$(_DELFINO_COMPLETE=bash_source delfino)";
}
complete -F _complete_delfino -o default invoke delfino
```

-->