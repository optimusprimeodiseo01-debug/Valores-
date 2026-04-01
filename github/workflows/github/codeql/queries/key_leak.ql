/**
 * Detecta posibles fugas de claves privadas
 */

import python

from StringLiteral s
where
  // patrones tipicos de clave privada
  s.getValue().regexpMatch("0x[a-fA-F0-9]{64}") or
  s.getValue().regexpMatch("PRIVATE_KEY") or
  s.getValue().regexpMatch("BEGIN PRIVATE KEY")
select s, "Posible clave privada hardcodeada detectada."
