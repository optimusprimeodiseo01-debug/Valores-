# SECURITY RULES - VALORES-

## Capas

1) almacenamiento
   key.txt + chmod 600

2) aislamiento
   signer separado

3) validacion
   limite de gas y valor

4) interfaz
   socket local (127.0.0.1)

5) repositorio
   .gitignore protege key.txt

6) comportamiento
   no imprimir secretos

---

## Reglas obligatorias

REGLA 1:
key.txt no se sube al repo

REGLA 2:
no claves en codigo

REGLA 3:
signer no expuesto a red externa

REGLA 4:
limite de valor en signer

REGLA 5:
rotar clave si hay duda

---

## Flujo seguro

clave → signer → firma → blockchain

robot no accede a la clave

---

## Definicion

seguridad = restriccion de flujo

la clave debe tener:

1 entrada
0 salidas
