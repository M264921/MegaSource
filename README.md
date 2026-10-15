# MegaSource

Agregador de metadatos de fuentes AltStore Classic. `build.py` descarga los JSON
de `sources.txt`, normaliza apps y escribe un unico array `apps`. No descarga IPA,
no instala apps y no importa certificados.

```powershell
python -m unittest discover -s tests -v
python build.py --dry-run
python build.py
```

Se mantienen las 22 URL historicas como lista editable. Algunas pueden haber
cambiado o no declarar los permisos que exige AltStore. El modo normal falla
si una fuente falla o hay entradas invalidas, y conserva el JSON anterior.
`--allow-partial` permite generar expresamente solo con las apps validas; revisa
`build-report.json` para saber cuales se han omitido. Si no queda ninguna app,
el generador siempre falla sin vaciar la salida.

La primera fuente de la lista tiene prioridad para un bundleIdentifier repetido
(sensible a mayusculas). Se conserva su objeto de permisos, restricciones y orden
de versiones; no se combinan versiones de otros publicadores bajo esos permisos.
Se aceptan versiones modernas y el formato plano antiguo cuando declara todos
los campos necesarios. Dentro de una app se deduplica version + buildVersion.
No se inventan permisos ni se usan imagenes inexistentes.

`--sources`, `--output` y `--report` permiten separar pruebas y resultado publicado.
La escritura del feed es atomica. El workflow comprueba fixtures en cada PR;
la actualizacion remota es manual y publica una rama/PR revisable, no modifica
automaticamente main. Pages debe servir main desde la raiz.

Formato contrastado con la [guia oficial de AltStore](https://faq.altstore.io/developers/make-a-source).
La validacion del JSON y las fixtures no certifican compatibilidad de cada app,
renovacion, firma ni instalacion en un iPhone. Hay que comprobarlo en el cliente.
