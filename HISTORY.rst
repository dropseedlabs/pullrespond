=======
History
=======

0.5.0 (2017-08-31)
------------------

* Added commands to create a label on a repo or all repos in an organization
* Add PR status and number of commits to PR tables


0.4.4 (2017-07-12)
------------------

* Fix missing prompt validator


0.4.3 (2017-07-12)
------------------

* Improved interactive prompt, including options and multi-commands
* Removed "enter-key speed mode"
* Exception for GraphQL errors


0.4.2 (2017-07-10)
------------------

* Fix ``sweep <org> pull`` no data


0.4.1 (2017-07-06)
------------------

* Add pagination
* Add bulk close pull requests
* Use re.search for pull request title matching


0.4.0 (2017-07-06)
------------------

* Make all commands actual click commands, then invoke them interactively if within sweep
* Add bulk pull request merging and closing per organization, filtering based on state or title


0.3.0 (2017-07-06)
------------------

* Add PR close command
* Refactor with ObjectPrompt class


0.2.0 (2017-07-05)
------------------

* Add files_changed
* Tables for display
* Add state to pull requests table


0.1.2 (2017-07-05)
------------------

* Rename to "sweep"


0.1.1 (2017-07-04)
------------------

* Fix missing submodules.


0.1.0 (2017-07-04)
------------------

* First release on PyPI.
