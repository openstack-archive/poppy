=======================================================
Implement a Horizon Plugin to work with Poppy's CDN API
=======================================================


Include the URL of your launchpad blueprint:


https://blueprints.launchpad.net/poppy/+spec/horizon


poppy needs to provide a horizon plugin to give to user capacity to use Poppy API through Horizon Dashboard


Problem description
===================

Currently Poppy does not provide a dedicated UI. it is only possible to use Poppy by using the Poppy API.
We would like to provide an Horizon plugin to work with Poppy CDN API and place the code on a dedicated repo.


Proposed change
===============

Create an openstack/poppy-ui project
Implement horizon plugin to manage CDN Services through Poppy API


poppy-ui  responsibilities
--------------------------

* Display a dedicated section in the Project dashboard 
* Display the list of existing CDN services
* Diplay the details of a CDN service
* Use Poppy API to manage CDN Services
* Use Poppy API to manage Domains
* Use Poppy API to manage Origin Servers
* Use Poppy API to manage Origin rules
* Use Poppy API to manage caching rules
* Use Poppy API to manage restriction

Projects
========

List the projects that this spec effects:

* openstack/poppy-ui

Implementation
==============

Milestones
----------

Target Milestone for completion:
  Mitaka

Work Items
----------

1) Create the poppy-ui repo on openstack-infra/project-config
2) Identified informations, panels and workflows to implement on the horizon plugin 
3) Create a Mock for review 
4) Create the poppy project on Invision 
5) Implements panels 

Dashboard Proposal
==================

"Content delivery" dashboard including the following panels:

* "Services" panel
* "Caching rules" panel
* "Service Details" panel (not reachable from menu)

Panels
------

"Services" panel 
~~~~~~~~~~~~~~~~

**Displayed information**

List in a table all existing services.

For each service following information should be displayed:

* Name of the Service
* Time since created
* CDN Provider
* Domains
* Origin servers
* Status
* An Action dropdown to interact with this service

**Actions**

From this view, users can:

* add a new service by clicking on the "Create service" button
* edit an existing service by clicking on "Edit Service" on Action dropdown 
* remove an existing service by selecting "delete service" on the corresponding Action dropdown
* remove several services by selecting checkbox of the corresponding services and clicking on the "delete service" button
* retrieve service details by clicking on the service name
* enable an existing service
* disable an existing service
* purge an exisiting service

"Caching rules" panel 
~~~~~~~~~~~~~~~~~~~~~

**Displayed information**

List in a table of existing caching rule for the project
For each caching rule, following information should be displayed:

* Name of the caching rule
* Applied path
* Details

**Actions**

From this view ,users can:

* display list of existing caching rules
* add a caching rule
* delete a caching rule
* delete several caching rules
* edit an existing caching rule

"Service Details" panel (not reachable from menu)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Displayed information**

Display following information for a service:

* Name of the service
* ID of the service 
* Project ID
* Status
* CDN Provider
* List in a table the linked Domains, with for each domain:

  * Domain Name
  * Certificate Type
  * Status
  * An Action dropdown to interact with this domain

* List in a table the linked Origin rules, with for each origin rule:

  * Name
  * Applied Path
  * Origin 
  * Host Header
  * An Action dropdown to interact with this origin rule

* List in a table the linked Caching rules, with for each caching rule:

  * Name
  * Applied Path
  * Origin Rules
  * Caching Rules
  * An Action dropdown to interact with this caching rule

* list in a table the linked  Restriction, with for each restriction:

  * Name
  * Type
  * Access
  * Applied path
  * Details
  * An Action dropdown to interact with this restriction

**Actions**

From this view users can:

* Add a Domain
* Remove a Domain
* Edit a Domain
* Add an Origin rules
* Remove an Origin rules
* Edit an Origin rules
* Add a caching rule
* Remove a caching rule
* Edit a caching rule
* Add a restriction
* Remove a restriction
* Edit a restriction

Workflows
---------

Add new service workflow
~~~~~~~~~~~~~~~~~~~~~~~~

A Popup called "create service" is displayed with the following tabs
* "details" tab. In this tab user has to specify:

  * The service Name
  * The Traffic type
  * The Certificate type
  * A Domain name
  * An Origin server


* "caching rule" tab. In this tab user can select the caching rule to apply, by default the checkbox of the "default" caching rule of the project is selected.


Edit an existing service Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By clicking on the "Edit Service" option of the action dropdown user can edit an existing service.
A Popup called Edit Services is displayed. the user can edit the name of the service or the state of the service and see the service ID

Remove an existing service Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By selecting "delete service" on the corresponding action dropdown, the user can delete a service.
A popup called "confirm delete service" is display. It informs the user that the operation cannot be undone and that the linked origins and domains are going to be deleted.

If user confirm, the service together with the domains and origins are deleted.

If user cancel, the service is not deleted.

Add a Domain workflow
~~~~~~~~~~~~~~~~~~~~~

by clicking on the "Create Domain" button, the user can create an Origin Rule.
A popup called "Create Domain" is displayed. The user has to specify:

* The Traffic type
* The Certificate Type.
* The Domain Name.

Two buttons are availabe:

* Create Domain
* Cancel

If "Create Domain" is selected, the Domain is created and linked to the service. 

If "Cancel is Selected" the Domain is not created.

The popup is closed and the service details panel is displayed.

Edit an Domain  workflow
~~~~~~~~~~~~~~~~~~~~~~~~

By selecting "Edit Domain" button the user can edit an Domain.
A Popup called "Edit Domain" is displayed. The user can edit:

* The Traffic type
* The Certificate Type
* The Domain Name

Two buttons are availabe:

* Submit
* Cancel

If "Submit" is selected, the Domain is updated.

If "Cancel is Selected" the Domain is not updated.

The popup is closed and the service details panel is displayed.

Remove a Domain workflow
~~~~~~~~~~~~~~~~~~~~~~~~

By selecting "delete Domain" on the corresponding action dropdown, the user can delete a Domain.
A popup called "confirm delete domain" is display. It informs the user that the operation cannot be undone.

If user confirm, the Domain is deleted.

If user cancel, the Domain is not deleted.

Add an Origin Rule workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

by clicking on the "Create Origin Rule" button, the user can create an Origin Rule.
A popup called "Create Origin Rule" is displayed. The user has to specify:

* The Name
* The Origin
* The Path

Two buttons are availabe:

* Create Origin Rule
* Cancel

If "Create Origin Rule" is selected, the Origin Rule is created and linked to the service.

If "Cancel is Selected" the Origin Rule is not created.

The popup is closed and the service details panel is displayed.

Edit an Origin Rule workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

by selecting "Edit Origin Rule" button the user can edit an Origin Rule.
A Popup called "Edit Origin Rule" is displayed. The user can edit:

* The Name
* The Path

Two buttons are availabe:

* Submit
* Cancel

If "Submit" is selected, the Origin Rule is updated.

If "Cancel is Selected" the Origin Rule is not updated.

The popup is closed and the service details panel is displayed.

Remove an origin rule workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By selecting delete origin rule on the corresponding action dropdown, the user can delete a origin rule.
a popup called "confirm delete origin rule" is display. It informs the user that the operation cannot be undone.

If user confirm, the origin rule is deleted.

If user cancel, the service is not deleted.

Add a caching rule workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

by clicking on the "Create Caching Rule" button the user can create a Caching Rule.
A Popup called "Create Caching Rule" is displayed. The user has to specify:

* The Name
* The TTL
* The Path

Two buttons are availabe:

* Create Caching Rule
* Cancel

If "Create Caching Rule" is selected, the Caching Rule is created and linked to the service. 

If "Cancel is Selected" the Caching Rule is not created.

The popup is closed and the service details panel is displayed.

Edit a Caching Rule workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By selecting "Edit Caching Rule" button the user can edit a restriction.
A Popup called "Edit Caching Rule" is displayed. The user can edit:

* The Name
* The TTL
* The Path

Two buttons are availabe:

* Submit
* Cancel

If "Submit" is selected, the Caching Rule is updated.

If "Cancel is Selected" the Caching Rule is not updated.

The popup is closed and the service details panel is displayed.

Remove a caching rule workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By selecting delete caching rule on the corresponding action dropdown, the user can delete a caching rule.
A popup called "confirm delete caching rule" is display. It informs the user that the operation cannot be undone.

If user confirm, the caching rule is deleted.

If user cancel, the caching rule is not deleted.

Add a restriction workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~

By clicking on the "Create Restriction" button the user can create a restriction.
A Popup called "Create Restriction" is displayed. The user has to specify:

* The Name
* The Type
* The Access
* The Referrer
* The Path

Two buttons are availabe:
* Create Restriction
* Cancel

If "Create Restriction" is selected, the Restriction is created and linked to the service. 

If "Cancel is Selected" the Restriction is not created.

The popup is closed and the service details panel is displayed.

Edit a restriction workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

by selecting "Edit Restriction" button the user can edit a restriction.
A Popup called "Edit Restriction" is displayed. The user can edit:

* The Name
* The Type
* The Access
* The Referrer
* The Path

Two buttons are availabe:

* Submit
* Cancel

If "Submit" is selected, the Restriction is updated.

If "Cancel is Selected" the Restriction is not updated.

The popup is closed and the service details panel is displayed.


Remove a restriction workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By selecting delete restriction on the corresponding action dropdown, the user can delete a restriction.
A popup called "confirm delete restriction" is displayed. It informs the user that the operation cannot be undone.

If user confirm, the restriction is deleted and removed from the restriction list.

If user cancel, the restriction is not deleted.

Purge a service workflow
~~~~~~~~~~~~~~~~~~~~~~~~

By selecting purge service on the corresponding action dropdown, the user can purge a service.
A popup called "confirm purge service" is displayed. It informs the user that the operation cannot be undone.

If user confirm, the service is purged.

If user cancel, the service is not purged.
