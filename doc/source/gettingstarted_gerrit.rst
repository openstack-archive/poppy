..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Using Gerrit
============

Before you begin
~~~~~~~~~~~~~~~~

To familiarize yourself with Poppy, try it out using the information in our [https://github.com/openstack/poppy repo]. When you are ready to start contributing, you will need to execute an [http://docs.openstack.org/infra/manual/developers.html#account-setup OpenStack CLA]. This is required before you can submit reviews to our [https://git.openstack.org/cgit/openstack/poppy Poppy StackForge Repo]. For information about how prepare for contribution, please consult the [http://docs.openstack.org/infra/manual/developers.html developer guide]].

Learn about Gerrit
------------------

Be sure to read the [[Gerrit_Workflow|Gerrit Workflow]] wiki page for information about how to submit your commit for review so it can be merged into the Poppy code base.

Setting up your git review settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  git config --global user.name "Firstname Lastname"
  git config --global user.email "your_email@youremail.com"
  git config --global gitreview.username "your_launchpad_username"

To check your git configuration:

  git config --list

Installing git-review
~~~~~~~~~~~~~~~~~~~~~

On Ubuntu, MacOSX, or most other Unix-like systems, use the following command:
  pip install git-review

There are other installation options detailed in the [[Gerrit_Workflow#Git_Review_Installation|Installation Instructions]]. You can now check out the Poppy code and begin working on it.

Your first commit
=================

Set up your local branch
~~~~~~~~~~~~~~~~~~~~~~~~

Use the following commands to set up your local branch:

  git clone git://git.openstack.org/openstack/poppy
  cd poppy
  git checkout -b [branch name]
  git review -s

Create a topic branch to hold your work and switch to it. If you are working on a blueprint, name your topic branch bp/BLUEPRINT where BLUEPRINT is the name of a blueprint in launchpad (for example, "bp/authentication"). The general convention when working on bugs is to name the branch bug/BUG-NUMBER (for example, "bug/1234567"). Otherwise, give it a meaningful name because it will show up as the topic for your change in Gerrit.

Write some awesome code
~~~~~~~~~~~~~~~~~~~~~~~

At this point can write your code and push it to Gerrit for review by using the following commands:

  git add <list of files you added/changed>
  git commit -a
  git review -v --draft

Once you are happy with your code and want it to be reviewed, you want to convert it from a Draft.   "Sign In" at https://review.openstack.org/ and after verifying the review yourself, hit the "Publish" button on the page.

If you know you are ready for others to review your code, you can skip the draft step and use:
 git review -v

If you want to revise your patchset in the review system in response to feedback, make your changes, then use:
 git commit -a --amend
 git review -v

Upon approval of the review, your code is automatically merged.

Reviews
-------

The OpenStack CI system uses the concept of core reviewers. These are individuals who have consistently reviewed code for the project, and helped over a considerable period of time to improve the quality and consistency of what we merge into the code base. Project contributors feel that this reviewer is a positive influence on the team and that they maintain the values and traditions of the OpenStack development community.

Policies
--------

Existing core reviewers may nominate new ones in an ML thread. Consent among the current reviewers shall result in the declaration of the new core reviewer by the PTL. Lack of unanimous consent shall be carefully considered, and a final decision informed by input from from active team members shall be made by the PTL. Core reviewers who are judged by their peers in the core review group to fall short of the expectations for contribution of a core reviewer may be nominated for return to regular reviewer status.

The current Gerrit policy is:

 label-Code-Review = -2..+2 group poppy-core
 label-Approved = +0..+1 group poppy-core

Patches require a core reviewer to mark a review as "Approved" before they are merged.

Review Guidelines
-----------------

Code Approval for Merge
~~~~~~~~~~~~~~~~~~~~~~~

* For Approval, two core reviewers shall supply a <code>+2</code>.

Continuing Someone Else's Contribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* If a patch submitted by one contributor is picked up and completed by another contributor, [http://www.mail-archive.com/openstack-dev@lists.openstack.org/msg05998.html special handling] of the resolution should be used.

Advice for Reviewers
~~~~~~~~~~~~~~~~~~~~

* A <code>-1</code> vote is an opportunity to make our code better before it is merged. Please do your best to make helpful, actionable -1 votes.
* Avoid the temptation to blindly <code>+1</code> code without reviewing it in sufficient detail to form an opinion.
* When voting <code>-1</code> on a patch, it means that you want the submitter to make a revision in accordance with your feedback before core reviewers should consider this code for merge.
* If you ask a question, you should vote <code>0</code> unless you anticipate that the answer to that question is likely to cause you to vote against the patch without further revisions.
* If you use a <code>-1</code> vote for a question, and the contributor answers the question, please respond acknowledging the question. Either change your vote or follow up with additional rationale for why this should remain a <code>-1</code> comment.
* A <code>-2</code> vote is a veto by a single core reviewer. It is sticky. That means that even if you revise your patch, that vote will persist. To allow your patch to merge, that same reviewer must clear the <code>-2</code> vote first. This vote is used when you have contributed something that is not in alignment with the current project vision, or is implemented in a way that can not be accepted. For example, security concerns that a core reviewer wants to individually re-evaluate before allowing the contribution to continue. It can also be used as a way to halt further gate testing of a patch, if something is included that may break the gate. It works even after a <code>2*+2,+A</code> approval for merge, but before the patch reaches MERGED state.
* To avoid a <code>-2</code> vote, discuss your plans with the development team prior to writing code, and post a WIP (workflow-1) patch while you are working on it, and ask for input before you submit it for merge review.

Testing
=======
See our [[Poppy/Testing]] wiki.
