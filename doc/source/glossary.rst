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

Glossary
========

Concepts
========
Poppy is an OpenStack-related project to provide a generic and modular vendor-neutral API that wraps provisioning instructions for CDN vendors that support it.

.. glossary::

   Caching Rule
     A caching rule provides the user with fine-grained control over the time-to-live (TTL) of an object. When the TTL expires for an object, the edge node pulls the object from the origin again.

   Domain
     A domain represents the domain name through which visitors retrieve content. The underlying site may be served through a CDN. A service can have multiple domains. A user typically uses CNAME for this domain to their CDN provider.

   Driver
     Poppy has a modular API where many components are interchangeable.  These components are known as drivers (see Stevedore Framework).  It is possible to use different transport drivers, manager drivers, storage drivers, and provider drivers.

   Edge Node
     CDN providers have many points-of-presence (POP) servers around the world.  These servers are known as edge nodes. These edge nodes cache the content and serve it directly to customers, thus reducing transit time to a customers location.

   Flavor
     A flavor allows the user to decide what CDN providers they would like their service to use.  Operators can define the flavors offered, and assign a CDN provider belonging to that flavor. Use flavors to abstract away the underlying provider used.

   Manager Driver
     A manager driver contains the business logic within the application. This driver is responsible for delegating tasks to Storage and Provider Drivers.

   Origin
     An origin is an address (ip or domain) from which the CDN provider pulls content. A service can have multiple origins.

   Provider
     There are many established CDN vendors in the market.  A provider is one of these vendors, who has decided to participate in the Poppy project.  These participating providers will have a provider driver that can communicate with their API.

   Provider Driver
     A provider driver is responsible for communicating with the third party providers who are participating in the Poppy project.

   Purge
     Purging removes content from the edge servers, so it can be refreshed from your origin servers.

   Restriction
     A restriction enables the user to define rules about who can or cannot access content from the cache. Examples of a restriction are allowing requests only from certain domains, geographies, or IP addresses.

   Service
     A service represents a customers' application that has its content cached to the edge nodes.

   Status
     The time it takes for a service configuration to be distributed amongst a CDN provider cache can vary.  The status indicates the current state of the service.

   Storage Driver
     A storage driver is responsible for communicating with the chosen data store to store service configurations.

   Transport Driver
     A transport driver handles the incoming requests to the API.  The recommended transport driver for Poppy is the Pecan Driver based on WSGI.
