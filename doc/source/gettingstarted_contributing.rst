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

Contributing to Poppy
=====================

First steps
-----------

Interested in contributing to Poppy? That's great to hear!

First of all, make sure to join our communication forums:

* Subscribe to our [[MailingLists|mailing lists]].
* Join us on IRC! You can chat with us directly in the '''#openstack-poppy''' channel on '''irc.freenode.org'''. Don't know to use IRC? You can find some directions in [[UsingIRC]] wiki page.
* Answer and ask questions on [https://ask.openstack.org/ Ask OpenStack].

How can I contribute?
---------------------

You can contribute to Poppy in many ways. Of course, coding is one, but you can also contribute as a tester, documenter, designer, or translator.

Coding
~~~~~~

Bug fixing and triaging
~~~~~~~~~~~~~~~~~~~~~~~

The first area where you can help is bug fixing. ''Confirmed'' bugs are usually your best choice. ''Triaged bugs'' should even contain tips on how you can fix them.

Once you selected the bug you want to work on, go ahead and assign it to yourself, branch the code, implement the fix, and propose your change for merging into trunk!

Some easy-to-fix bugs may be marked with the '''low-hanging-fruit''' tag. Those are good targets for a beginner.

Reported bugs need care: prioritizing them correctly, confirming them, making sure they don't go stale... All those tasks help immensely. If you want to start contributing in coding but you are not a hardcore developer, consider helping in this area!

Bugs can be marked with different tags according to their status, as follows:
* ''New'' bugs are those bugs that have been reported by a user but haven't been verified by the community yet.
* ''Confirmed'' bugs are those bugs that have been reproduced by someone else than the reporter.
* ''Triaged'' bugs are those bugs that have been reproduced by a core developer.
* ''Incomplete'' bugs are those bugs that don't have enough information to be reproduced.
* ''In Progress'' bugs are those bugs that are being fixed by a developer.
* ''Invalid'' bugs are those bugs that don't qualify as a bug. These usually stem from a support request or something unrelated to the project.


You can learn more, see Launchpad's [http://blog.launchpad.net/general/of-bugs-and-statuses Of Bugs and Statuses].

You only have to worry about ''New'' bugs. If you can reproduce them, you can mark them as ''Confirmed''. If you cannot reproduce them, you can ask the reporter to provide more information and mark them as ''Incomplete''. If you think that they aren't bugs, mark them as "Invalid". (Be careful! Asking someone else in Poppy is always a good idea.)

Also, you can contribute instructions about how to fix a given bug.

Check out the [[BugTriage|Bug Triage]] wiki for more information.

Reviewing
~~~~~~~~~

Every patch submitted to OpenStack gets reviewed before it can be approved and merged. We get a lot of contributions and everyone can - and is encouraged! [https://review.openstack.org/#/q/status:open+project:openstack/poppy,n,z Review Poppy's existing patches]. Pick an open review and go through it. Test it if possible, and leave a comment with a +1 or -1 vote describing what you discovered. If you're planning to submit patches of your own, this is a great way to learn about what the community cares about and to learn about the code base.

Feature development
~~~~~~~~~~~~~~~~~~~

Once you get familiar with the code, you can start to contribute new features. New features get implemented every 6 months in a [[ReleaseCycle|development cycle]]. We use Launchpad [[Blueprints]] to track the design and implementation of significant features, and we use Design Summits every 6 months to discuss them in public. Code should be proposed for inclusion before we reach the final feature milestone of the development cycle.

Testing
~~~~~~~

Testing efforts are highly related to coding. If you find that there are test cases missing or that some tests could be improved, you are encouraged to report it as a bug, and then provide your fix. Learn more about this in Write The Tests!

Documenting
~~~~~~~~~~~

You can contribute to Poppy's Users Guide and Poppy's Wiki. See Documentation/HowTo for details, as well as Documentation/HowTo/FirstTimers, which has some other info that may be useful.

To fix a documentation bug, check the bugs marked with the 'doc' tag in Poppy's [https://bugs.launchpad.net/poppy/+bugs?field.tag=doc bug list]. In case that you want to report a documentation bug, then don't forget to add the 'doc' tag to it :)

You can also start by reading the developer documentation which is created using Sphinx as part of the code in the /doc/source/ directory and published to [https://poppy.readthedocs.org Read The Docs].

Also, monitor [http://ask.openstack.org Ask OpenStack] to curate the best answers that can be folded into the documentation.
