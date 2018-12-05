source subtreeRemote

git subtree pull --prefix=cogs --squash --message="update cogs subtree" $COGS_REPOSITORY $COGS_BRANCH
git push origin HEAD
