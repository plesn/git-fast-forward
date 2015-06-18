git-ff : simple fast forward without working tree
-------------------------------------------------

Fast forward branches without checking-out, works by looking if the
branch is an ancestry of the tracking branch and upating the ref.

- can fast-forward branches on a bare repository
- can fast-forward all tracking branches possible
- does not do anything when no fast forward (merge or push required)

use an alias in .gitconfig:

    [alias]
        ff = !git-ff "$@"

examples
--------

fast forward current branch:

    $ git ff
    heads/v1.8           [remotes/ompi/v1.8]       : behind 4
      fast-forwarding d241021..e86824f

fast forward all branches possible:

    $ git ff --all
    heads/master         [remotes/ompi/master]     : behind 22
      fast-forwarding c33b786..7068846
    heads/v1.8           [remotes/ompi/v1.8]       : behind 4
      fast-forwarding d241021..e86824f
    heads/v1.8-mine      [remotes/release/v1.8]    : ahead 1
      you can push: git push release heads/v1.8-mine:v1.8



see which branches can advance (like in `git branch -avv`)

    $ git ff --status
    heads/master         [remotes/ompi/master]     : behind 22
    heads/v1.8           [remotes/ompi/v1.8]       : behind 4
    heads/v1.8-mine      [remotes/release/v1.8]    : ahead 1


