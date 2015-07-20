#!/usr/bin/python

"""
git-ff [options] [<branch>]

 fast-forward <branch> (or by default current branch)

 fast-forward without trying to merge : just update the
 reference. Usefull especially without working directory.
 
 usage:
  -h | --help
  -s | --status  : show merge state of all branches
  -a | --all     : fast forward all branches
"""


from subprocess import Popen, PIPE, CalledProcessError
import sys
import getopt

## not finished

def sh(cmd):
    "call shell command, in python 2.6+. strip eol."
    p = Popen(cmd, shell=True, stdout=PIPE)
    if p.wait() != 0: raise CalledProcessError(p.returncode, cmd)
    return p.stdout.read().strip('\n')


def is_ancestor(a, b):
    "if commit a is ancestor of commit b"
    common = sh("git merge-base %s %s " % (a, b))
    return common == sh("git rev-parse %s" % a)

def merge_status(ref, up):
    "merge status with upstream : up-to-date | behind n | ahead n | merge required"
    if sh("git rev-parse %s"%ref) == sh("git rev-parse %s"%up):
        return "up-to-date"
    elif is_ancestor(ref, up):
        n = len(sh("git rev-list %s..%s"%(ref,up)).splitlines())
        return "behind %d" % n
    elif is_ancestor(up, ref):
        n = len(sh("git rev-list %s..%s"%(up,ref)).splitlines())
        return "ahead %d" % n
    else:
        return "merge/rebase required"

def all_status():
    "print merge status of all branches"
    refs = sh("git for-each-ref --shell --format='(%(refname),%(upstream))' refs/heads/")
    for l in refs.splitlines():
        ref, up = eval(l)
        if up != "":
            status = merge_status(ref, up)
            print "%-20s: [%s: %s]" % (ref, up, status)
        else:
            print "%-20s: not tracking" % ref


def git_ff(branch):
    "fast forward branch if needed (update the ref)"
    if branch is None:
        # take current branch
        branch = sh("git rev-parse --abbrev-ref HEAD")
    try: branch = sh("git show-ref --heads %s" % branch).split()[1]
    except: sys.exit("error: branch %s does not exist" % branch)
    branch_sha = sh("git rev-parse --verify -q %s"%branch)

    try: upstream = sh("git rev-parse --symbolic-full-name"
                  " --verify -q %s@{upstream} 2>/dev/null"
                  % branch[len("refs/heads/"):])
    except: sys.exit("error: no upstream for branch %s" % branch)

    status = merge_status(branch, upstream)
    print "%-20s %-25s : %-s" % (branch[len("refs/"):],
                                 upstream[len("refs/"):], status)
    if status.startswith("behind"):
        print "  fast-forwarding %s..%s" % (
            sh("git rev-parse --short %s"%branch),
            sh("git rev-parse --short %s"%upstream))
        sh("git update-ref %s %s" % (branch, upstream))
        return 0
    elif status.startswith("ahead"):
        remote, upref = upstream[len("refs/remotes/"):].split("/", 1)
        print "  you can push: git push %s %s:%s" %(remote, branch[len("refs/"):], upref)
        return 0
    elif status == "up-to-date":
        return 0
    else:
        return 1
    

def git_ff_all():
    "fast forward all tracking branches"
    refs = sh("git for-each-ref --shell --format='(%(refname),%(upstream))' refs/heads/")
    for l in refs.splitlines():
        ref, up = eval(l)
        if up != "":
            git_ff(ref)

def _test():
    print "faulty rev-parse:"
    try:
        print sh("git rev-parse --verify feb0f"),
    except CalledProcessError, e:
        print "rev-parse failed:", e

    print "all status:"
    all_status()
    print
    branch = "ruby"
    print "gitff %s" % branch
    git_ff(branch)

def main(argv):
    opts, args = getopt.getopt(argv, "hsa", ["help", "status", "all"])
    opts = dict(opts)
    if '-h' in opts or '--help' in opts:
        sys.exit(__doc__.strip())
    elif '-s' in opts or '--status' in opts:
        all_status()
    elif '-a' in opts or '--all' in opts:
        git_ff_all()
    else:
        branch = args[0] if len(args)>0 else None
        #branch = None
        git_ff(branch)

if __name__ == '__main__':
    #_test()
    main(sys.argv[1:])

    
