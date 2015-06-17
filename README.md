Simple fast forward without working tree.

Works on a bare reository

fast forward current branch:

    $ git ff

advance all branches

    $ git ff --all

see which branches can advances (like in `git branch -avv`

    $ git ff --status

use an alias in .gitconfig:

    [alias]
        ff = !git-ff "$@"
