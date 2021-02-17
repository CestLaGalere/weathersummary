# EauFrance station data

## Installation

To install this integration you will need to add <https://github.com/cestlagalere/eaufrance> as a custom repository in HACS.

Once installed you will be able to install the integration from the HACS integrations page.

Restart your Home Assistant to complete the installation.

## Configuration

Go to Configuration -> Integrations and click the plus sign to add a Eaufrance integration. Search for Eaufrance and click add.

add elements to yaml sensor section:
  \- platform: eaufrance
    name: montauban_flow
    device_class: Q
    device_id: O494101001

device_class - Q (Quantity of water - in m3 / s) H - river height (m)
device_id: id of the station
see either
<https://hubeau.eaufrance.fr/api/v1/hydrometrie/referentiel/sites>
or the map at:
<https://www.vigicrues.gouv.fr/niv2-bassin.php?CdEntVigiCru=25>

<https://hubeau.eaufrance.fr/api/v1/hydrometrie/api-docs>
