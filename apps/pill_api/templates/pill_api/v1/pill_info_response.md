{% for drug in drugs %}
## {{ drug.name }}
{% if drug.image_url %}![{{ drug.name }}]({{ drug.image_url }}){% endif %}

| **Drug Information**  |                                                                             |
|---|---|
| **National Drug Code** | {{ drug.ndc }}                                                              |
| **Shape**             | {{ drug.shape                                                               |capfirst }} |
| **Colors**            | {{ drug.colors                                                              |join:", "|capfirst }} |
| **Imprints**          | {{ drug.imprints                                                            |join:", "|upper }} |
| **Usage**             | Explain what the drug is used to treat                                      |    
| **Warnings**          | Explain any warnings or DEA schedule information associated with the drug   |

{% endfor %}