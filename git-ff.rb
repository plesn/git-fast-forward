#!/usr/bin/ruby

#   Simple fast-forward without working tree
#   ruby version

#   Advances the branch ref if it is and ancestror of target.
#   No need of a working tree as it does not try to merge but uses git
#   merge-base.
#
#   use an alias in .gitconfig:
#     ff   = !git-ff "$@"
#
#   author: piotr.lesnicki@ext.bull.net



def ancestor?(a, b)
  common = `git merge-base #{a} #{b}`
  return common == `git rev-parse #{a}`
end

def merge_status(ref, up)
  if `git rev-parse #{ref}` == `git rev-parse #{up}`
    return "up-to-date"
  elsif ancestor? ref, up
    n = `git rev-list #{ref}..#{up}`.lines.count
    return "behind #{n}"
  elsif ancestor? up, ref
    n = `git rev-list #{up}..#{ref}`.lines.count
    return "ahead #{n}"
  else
    return "merge/rebase required"
  end
end

def all_status()
    r = `git for-each-ref --shell --format='ref=%(refname); up=%(upstream);' refs/heads/`
    fail if $?.to_i != 0
    r.lines do |l|
      ref=nil; up=nil
      eval l
      if up != ""
        status = merge_status ref, up
        puts "#{'%-20s'%ref}: [#{up}: #{status}]"
      else
        puts "#{'%-20s'%ref}: not tracking"
      end
    end
end

def ff(branch)
  if branch == ""
    branch = `git rev-parse --abbrev-ref HEAD`
  end

  `git show-ref --heads -q #{branch}`
  if $?.to_i != 0
    raise "branch #{branch} is not a local head reference"
  end
  branch = `git show-ref --heads #{branch}`.lines.collect{ |l| l.split[1]}[0]

  branch_sha = `git rev-parse --verify -q #{branch}`
  if $?.to_i != 0; raise "error: branch #{branch} invalid" end

  branchname = branch.sub("refs/heads/","")
  upstream = `git rev-parse --symbolic-full-name --verify -q \
                #{branchname}@{upstream} 2>/dev/null`.strip
  if $?.to_i !=0; raise "error: not tracking anything" end

  status = merge_status branch, upstream
  puts "#{branch.sub("refs/","")} [#{upstream.sub("refs/","")}: #{status}]"
  if status.include? "behind"
    puts "  fast-forwarding %s..%s" \
    % [`git rev-parse --short #{branch}`.strip, `git rev-parse --short #{upstream}`.strip]
    `git update-ref #{branch} #{upstream}`
    if $?.to_i !=0; raise "error: update ref #{branch} to #{upstream} failed" end
  elsif status.include? "ahead"
    remote = upstream.sub("refs/remotes/","").split("/")[0]
    upref = upstream.sub("refs/remotes/","").split("/")[1..-1]
    puts "  you can push: git push #{remote} #{branch.sub("refs/","")}:#{upref}"
  elsif status.include? "up-to-date"
  elsif status.include "merge"
    puts "  merge/rebase required"
  else
    raise "  bad status"
  end
    
end

def ff_all()
  r=`git for-each-ref --shell --format='ref=%(refname); up=%(upstream);' refs/heads/`
  if $?.to_i !=0; raise "error: for-each-ref failed" end
  r.lines do |l|
    ref=nil; up=nil;
    eval l
    if up != ""
      ff ref
    end
  end
end


def main()
    if (ARGV.include? '-h' or ARGV.include? '--help')
      $stderr.puts "usage: <branch> || --all || --status"
      $stderr.puts "  fast-forward branch <branch>"
      exit 1
    end
    arg = ARGV[0]
    if arg == '--status'
      all_status
    elsif arg == '--all'
      ff_all
    elsif arg and arg != ''
      ff arg
    else
      puts "nothing"
    end
end


if __FILE__ == $0
  main
end
