import utils
from tools import home, github, bitbucket

cd = utils.cd

commands = (
    "add", "am", "annotate", "apply", "archive", "bisect", "blame",
    "branch", "bundle", "checkout", "cherry", "cherry-pick", "clean",
    "clone", "commit", "config", "describe", "diff", "difftool",
    "fetch", "filter-branch", "format-patch", "fsck", "gc",
    "get-tar-commit-id", "grep", "help", "imap-send", "init",
    "instaweb", "interpret-trailers", "log", "merge", "mergetool",
    "mv", "name-rev", "notes", "pull", "push", "rebase", "reflog",
    "remote", "repack", "replace", "request-pull", "reset",
    "revert", "rm", "shortlog", "show", "show-branch", "stage",
    "stash", "status", "submodule", "subtree", "tag", "verify-commit",
    "whatchanged", "worktree",
)

git = utils.subcommands("git", *commands)

repos = {
    "insar_meteo": github.join("insar_meteo"),
    "geodynamics": github.join("geodynamics"),
    "utils": github.join("utils"),
    "texfiles": home.join("Dokumentumok", "texfiles"),
    "pygamma": github.join("pygomma"),
}


class Git(cd):
    default_user = "bozso"
    
    tpl = 
    
    __slots__ = (
        "path",
    )
    
    def __init__(self, repo_path):
        self.path = repo_path
        cd.__init__(self, repo_path)
    
    def __enter__(self):
        cd.__enter__(self)
        
        return self
    
    def report(self, repo):
        pass
        
        
def main():
    for repo, path in repos.items():
        
        with Git(path) as g:
            print(git.push().decode("utf-8"))
    
        
if __name__ == "__main__":
    main()
